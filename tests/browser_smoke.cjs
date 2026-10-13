"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const html = fs.readFileSync("web/index.html", "utf8");
const match = html.match(/<script>([\s\S]*?)<\/script>/i);
assert(match, "Expected an inline JavaScript application");
const stub = { addEventListener() {}, disabled: false };
const sandbox = {
  document: { getElementById() { return stub; } },
  console
};
vm.createContext(sandbox);
vm.runInContext(match[1], sandbox, {filename: "web/index.html"});
const evaluate = (payload) => vm.runInContext("localAudit(" + JSON.stringify(payload) + ")", sandbox);
const base = {
  task_id: "SYNTH-TEST",
  target_identifier: "SYNTH-TARGET",
  primary_metric: 15,
  secondary_metric: 2,
  status_descriptor: "NORMAL",
  is_critical_flag: false
};
const normal = evaluate(base);
assert.equal(normal.overall_urgency, "ROUTINE");
assert.equal(normal.total_alerts, 0);
assert.equal(normal.audit_hash, null);
const elevated = evaluate({...base, primary_metric: 26, secondary_metric: 13, status_descriptor: "DISCORDANT"});
assert.equal(elevated.overall_urgency, "ELEVATED_RISK");
assert.equal(elevated.total_alerts, 3);
const critical = evaluate({...base, is_critical_flag: true});
assert.equal(critical.overall_urgency, "CRITICAL_STAT_PANIC");
assert.equal(critical.critical_alerts_count, 1);
console.log("Browser demonstration rule smoke tests passed.");
