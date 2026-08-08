#!/usr/bin/env node

import {readFile, writeFile} from 'node:fs/promises';

const [url, output, statePath, clickLabel] = process.argv.slice(2);
if (!url || !output) {
  throw new Error('usage: capture_cdp.mjs URL OUTPUT.png [browser-state.json]');
}

const targets = await fetch('http://127.0.0.1:9224/json/list').then((response) => response.json());
const target = targets.find((entry) => entry.type === 'page');
if (!target) throw new Error('No Chrome page target on CDP port 9224');

const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  socket.addEventListener('open', resolve, {once: true});
  socket.addEventListener('error', reject, {once: true});
});

let nextId = 0;
const pending = new Map();
socket.addEventListener('message', (event) => {
  const message = JSON.parse(event.data);
  if (!message.id || !pending.has(message.id)) return;
  const {resolve, reject} = pending.get(message.id);
  pending.delete(message.id);
  if (message.error) reject(new Error(JSON.stringify(message.error)));
  else resolve(message.result);
});

const send = (method, params = {}) => new Promise((resolve, reject) => {
  const id = ++nextId;
  pending.set(id, {resolve, reject});
  socket.send(JSON.stringify({id, method, params}));
});

await send('Page.enable');
await send('Runtime.enable');
await send('Network.enable');
await send('Emulation.setDeviceMetricsOverride', {
  width: 1920,
  height: 1080,
  deviceScaleFactor: 2,
  mobile: false,
  screenWidth: 1920,
  screenHeight: 1080,
});

if (statePath) {
  const state = JSON.parse(await readFile(statePath, 'utf8'));
  const cookies = state.cookies.map((cookie) => ({
    name: cookie.name,
    value: cookie.value,
    domain: cookie.domain,
    path: cookie.path ?? '/',
    secure: cookie.secure ?? false,
    httpOnly: cookie.httpOnly ?? false,
    sameSite: cookie.sameSite,
    expires: cookie.expires > 0 ? cookie.expires : undefined,
  }));
  await send('Network.setCookies', {cookies});
}

await send('Page.navigate', {url});
await send('Runtime.evaluate', {
  expression: 'new Promise((resolve) => setTimeout(resolve, 5000))',
  awaitPromise: true,
  returnByValue: true,
});
if (clickLabel) {
  for (const action of clickLabel.split('|')) {
    if (action.startsWith('coord:')) {
      const [x, y] = action.slice('coord:'.length).split(',').map(Number);
      await send('Input.dispatchMouseEvent', {type: 'mousePressed', x, y, button: 'left', clickCount: 1});
      await send('Input.dispatchMouseEvent', {type: 'mouseReleased', x, y, button: 'left', clickCount: 1});
    } else if (action.startsWith('testid:') || action.startsWith('selector:')) {
      const isTestId = action.startsWith('testid:');
      const target = action.slice(action.indexOf(':') + 1);
      const clickResult = await send('Runtime.evaluate', {
        expression: `(() => {
          const target = ${JSON.stringify(target)};
          const selector = ${isTestId} ? '[data-testid="' + CSS.escape(target) + '"]' : target;
          const element = document.querySelector(selector);
          if (!element) throw new Error('missing selector: ' + selector);
          element.click();
          return true;
        })()`,
        returnByValue: true,
      });
      if (clickResult.exceptionDetails) throw new Error(JSON.stringify(clickResult.exceptionDetails));
    } else {
      const clickResult = await send('Runtime.evaluate', {
        expression: `(() => {
          const label = ${JSON.stringify(action)};
          const element = [...document.querySelectorAll('button,[role="tab"],a,span')]
            .find((item) => item.textContent.trim() === label);
          if (!element) throw new Error('missing clickable label: ' + label);
          element.click();
          return true;
        })()`,
        returnByValue: true,
      });
      if (clickResult.exceptionDetails) throw new Error(JSON.stringify(clickResult.exceptionDetails));
    }
    await send('Runtime.evaluate', {
      expression: 'new Promise((resolve) => setTimeout(resolve, 3000))',
      awaitPromise: true,
      returnByValue: true,
    });
  }
}
const result = await send('Page.captureScreenshot', {
  format: 'png',
  fromSurface: true,
  captureBeyondViewport: false,
});
await writeFile(output, Buffer.from(result.data, 'base64'));
socket.close();

console.log(JSON.stringify({url, output, width: 3840, height: 2160}));
