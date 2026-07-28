import base64
import json
import os
import subprocess
import tempfile
import time
import urllib.request

import websocket


ROOT = os.path.dirname(os.path.abspath(__file__))
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCREENSHOT = os.path.join(ROOT, "swagger-crud-results.png")


def wait_for(url, attempts=60):
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                return response.read()
        except Exception:
            time.sleep(0.25)
    raise RuntimeError(f"Timed out waiting for {url}")


server = subprocess.Popen(
    [
        os.sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ],
    cwd=ROOT,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
)

profile = tempfile.TemporaryDirectory(prefix="task-api-edge-")
edge = None
ws = None

try:
    wait_for("http://127.0.0.1:8000/health")
    edge = subprocess.Popen(
        [
            EDGE,
            "--headless=new",
            "--remote-debugging-port=9222",
            "--remote-allow-origins=*",
            f"--user-data-dir={profile.name}",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=1600,1200",
            "http://127.0.0.1:8000/docs",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    wait_for("http://127.0.0.1:9222/json")

    pages = json.loads(wait_for("http://127.0.0.1:9222/json"))
    page = next(item for item in pages if item.get("type") == "page")
    ws = websocket.create_connection(
        page["webSocketDebuggerUrl"], timeout=120, suppress_origin=True
    )
    message_id = 0

    def command(method, params=None):
        nonlocal_id = None
        global message_id
        message_id += 1
        nonlocal_id = message_id
        ws.send(json.dumps({"id": nonlocal_id, "method": method, "params": params or {}}))
        while True:
            response = json.loads(ws.recv())
            if response.get("id") == nonlocal_id:
                if "error" in response:
                    raise RuntimeError(response["error"])
                return response.get("result", {})

    command("Page.enable")
    command("Runtime.enable")
    command(
        "Emulation.setDeviceMetricsOverride",
        {"width": 1600, "height": 1200, "deviceScaleFactor": 1, "mobile": False},
    )

    script = r"""
    (async () => {
      const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
      const waitFor = async (selector, root = document, timeout = 20000) => {
        const start = Date.now();
        while (Date.now() - start < timeout) {
          const found = root.querySelector(selector);
          if (found) return found;
          await sleep(100);
        }
        throw new Error('Timed out waiting for ' + selector);
      };
      const setValue = (element, value) => {
        const setter = Object.getOwnPropertyDescriptor(
          Object.getPrototypeOf(element), 'value'
        ).set;
        setter.call(element, value);
        element.dispatchEvent(new Event('input', {bubbles: true}));
        element.dispatchEvent(new Event('change', {bubbles: true}));
      };
      const run = async (path, method, body, taskId) => {
        const selector = `.opblock[data-path="${path}"][data-method="${method}"]`;
        const block = await waitFor(selector);
        if (!block.classList.contains('is-open')) {
          block.querySelector('.opblock-summary-control').click();
          await sleep(250);
        }
        const tryButton = await waitFor('button.try-out__btn', block);
        if (/try it out/i.test(tryButton.textContent)) {
          tryButton.click();
          await sleep(250);
        }
        if (taskId !== undefined) {
          const input = await waitFor('.parameters input', block);
          setValue(input, String(taskId));
        }
        if (body !== undefined) {
          const textarea = await waitFor('textarea', block);
          setValue(textarea, JSON.stringify(body, null, 2));
        }
        const execute = await waitFor('button.execute', block);
        execute.click();
        const start = Date.now();
        while (Date.now() - start < 20000) {
          const status = block.querySelector('.response-col_status');
          const loading = block.querySelector('.loading-container');
          if (status && /^(200|201|204)$/.test(status.textContent.trim()) && !loading) break;
          await sleep(150);
        }
        await sleep(250);
        return block;
      };

      await waitFor('.swagger-ui');
      const create = await run('/tasks', 'post', {title: 'Swagger screenshot task', done: false});
      const list = await run('/tasks', 'get');
      const update = await run('/tasks/{task_id}', 'put', {title: 'Updated in Swagger', done: true}, 4);
      const remove = await run('/tasks/{task_id}', 'delete', undefined, 4);

      const keep = new Set([create, list, update, remove]);
      document.querySelectorAll('.opblock').forEach(block => {
        if (!keep.has(block)) block.style.display = 'none';
      });
      document.querySelectorAll('.information-container, .scheme-container, .models, .topbar').forEach(
        node => node.style.display = 'none'
      );
      keep.forEach(block => {
        block.querySelectorAll('.opblock-description-wrapper, .opblock-section-request-body, .parameters-container').forEach(
          node => node.style.display = 'none'
        );
      });
      const style = document.createElement('style');
      style.textContent = `
        body { background: white !important; }
        .swagger-ui .wrapper { max-width: 1500px !important; padding-top: 20px !important; }
        .swagger-ui .opblock { margin: 0 0 16px !important; }
        .swagger-ui .opblock-body { padding: 0 12px 10px !important; }
        .swagger-ui table { margin: 6px 0 !important; }
        .swagger-ui .responses-inner { padding: 8px 12px !important; }
      `;
      document.head.appendChild(style);
      window.scrollTo(0, 0);
      await sleep(500);

      return [...keep].map(block => ({
        method: block.dataset.method,
        path: block.dataset.path,
        status: block.querySelector('.response-col_status')?.textContent.trim() || 'missing'
      }));
    })()
    """
    result = command(
        "Runtime.evaluate",
        {"expression": script, "awaitPromise": True, "returnByValue": True},
    )
    value = result.get("result", {}).get("value")
    if not value:
        details = result.get("exceptionDetails") or result
        raise RuntimeError(f"Swagger automation failed: {details}")
    expected = {("post", "/tasks", "201"), ("get", "/tasks", "200"),
                ("put", "/tasks/{task_id}", "200"),
                ("delete", "/tasks/{task_id}", "204")}
    actual = {(item["method"], item["path"], item["status"]) for item in value}
    if actual != expected:
        raise RuntimeError(f"Unexpected Swagger results: {value}")

    dimensions = command(
        "Runtime.evaluate",
        {
            "expression": "({width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight})",
            "returnByValue": True,
        },
    )["result"]["value"]
    shot = command(
        "Page.captureScreenshot",
        {
            "format": "png",
            "captureBeyondViewport": True,
            "clip": {
                "x": 0,
                "y": 0,
                "width": min(1600, dimensions["width"]),
                "height": dimensions["height"],
                "scale": 1,
            },
        },
    )
    with open(SCREENSHOT, "wb") as output:
        output.write(base64.b64decode(shot["data"]))
    print(json.dumps(value))
    print(SCREENSHOT)
finally:
    if ws is not None:
        ws.close()
    if edge is not None:
        edge.terminate()
        try:
            edge.wait(timeout=5)
        except subprocess.TimeoutExpired:
            edge.kill()
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
    profile.cleanup()
