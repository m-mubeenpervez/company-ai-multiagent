# CompanyAI evaluation

Use the Python 3.12 `.venv-eval` environment. The authoritative commands, metric
definitions, checkpoint provenance and quota controls are in the
[evaluation guide](../evaluations/EVALUATION_GUIDE.md).
Run suites sequentially; do not bypass an account-matching open quota circuit.
RAGAS has six cases; DeepEval has 18 original plus two denial cases; routing has
36; separate agent acceptance has 18 workflows, four missing-input and two denial
cases. Live injection acceptance has three cases: user, document and MCP output.
Offline tests, model test doubles and historical results are not live acceptance.
