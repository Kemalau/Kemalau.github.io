// Typeset at build time so equations remain readable without client-side JS.
const fs = require("node:fs");
const katex = require("katex");

const formulas = JSON.parse(fs.readFileSync(0, "utf8"));
const rendered = formulas.map(({ latex, display }) => katex.renderToString(latex, {
  displayMode: display,
  output: "htmlAndMathml",
  throwOnError: true,
  strict: "error",
  trust: false,
}));
process.stdout.write(JSON.stringify(rendered));
