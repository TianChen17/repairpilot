#!/usr/bin/env node

import {mkdir, writeFile} from 'node:fs/promises';
import path from 'node:path';

const outputDirectory = process.argv[2];
if (!outputDirectory) throw new Error('usage: capture_repairpilot_journey.mjs OUTPUT_DIRECTORY');
await mkdir(outputDirectory, {recursive: true});

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
const evaluate = async (expression, awaitPromise = false) => {
  const result = await send('Runtime.evaluate', {expression, awaitPromise, returnByValue: true});
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
};
const delay = (milliseconds) => evaluate(`new Promise((resolve)=>setTimeout(resolve,${milliseconds}))`, true);
const waitForText = async (text, timeoutMs = 60000) => {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (await evaluate(`document.body.innerText.includes(${JSON.stringify(text)})`)) return;
    await delay(500);
  }
  throw new Error(`Timed out waiting for ${text}`);
};
const clickText = async (text) => evaluate(`(() => {
  const element = [...document.querySelectorAll('button,a')].find((item)=>item.textContent.includes(${JSON.stringify(text)}));
  if (!element) throw new Error('missing clickable: ' + ${JSON.stringify(text)});
  element.click();
  return true;
})()`);
const screenshot = async (name) => {
  const result = await send('Page.captureScreenshot', {format: 'png', fromSurface: true, captureBeyondViewport: false});
  await writeFile(path.join(outputDirectory, name), Buffer.from(result.data, 'base64'));
};

await send('Page.enable');
await send('Runtime.enable');
await send('Network.enable');
await send('Emulation.setDeviceMetricsOverride', {width:1920,height:1080,deviceScaleFactor:2,mobile:false,screenWidth:1920,screenHeight:1080});
await send('Page.navigate', {url:'https://repairpilot.145-241-207-154.sslip.io'});
await delay(2500);
await screenshot('repairpilot-ready-2x.png');
await clickText('New run / Reset');
await waitForText('Demo reset');
await clickText('Run live incident');
await waitForText('Go to approval');
await screenshot('repairpilot-awaiting-2x.png');
await evaluate("document.querySelector('#approval').scrollIntoView({block:'center'})");
await delay(500);
await screenshot('repairpilot-approval-2x.png');
await clickText('Approve repair');
await waitForText('The next incident starts smarter');
await evaluate("document.querySelector('#writeback').scrollIntoView({block:'center'})");
await delay(500);
await screenshot('repairpilot-learned-2x.png');
const resetResponse = await fetch('https://repairpilot.145-241-207-154.sslip.io/api/v1/demo/reset', {method:'POST'});
if (!resetResponse.ok) throw new Error(`Final demo reset failed: ${resetResponse.status}`);
socket.close();

console.log(JSON.stringify({status:'LEARNED',finalReset:true,width:3840,height:2160,outputDirectory}));
