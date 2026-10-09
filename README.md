The Sequential Matching Problem — Hackathon Working Repository
IIT Madras × RomeoJulietLove Hackathon | Vouchsafe | Final participant release 1.0.0
> **Attribution note:** This repository is my working copy of the official Sequential Matching Problem starter project. The original challenge, simulator, dataset, and starter implementation were created by the challenge author, [RomeoJulietLove](https://github.com/RomeoJulietLove/The-Sequential-Matching-Problem). I am using the existing codebase to run experiments and develop my hackathon submission. This is not a claim that I created the original project or its underlying algorithms.
What is this?
The Sequential Matching Problem is a simulated matching challenge. A policy must decide who to introduce, when to wait, and what information to clarify while working with incomplete preferences, reciprocal constraints, and feedback that may arrive later.
The people, profiles, conversations, and outcomes in the supplied simulator are synthetic. This repository is being used for my model-analysis and hackathon work, including running the provided baselines, comparing results, and experimenting with policy changes.
Official upstream repository: RomeoJulietLove/The-Sequential-Matching-Problem
Official problem statement: PROBLEM_STATEMENT.md
Official submission instructions: docs/SUBMISSION.md
Run it locally
You need Python 3.10 or later. The starter project has no external Python dependencies.
Clone or download this repository.
Open a terminal in the repository folder.
Run the checks and a small evaluation:
```bash
python -m unittest -v
python verify_data.py
python evaluate.py --seeds 101 --output results/first_run.json
```
On Windows, use `py` instead of `python` if necessary. On macOS or Linux, use `python3` if that's how Python is installed.
The evaluator writes results to the JSON path you specify. The scores describe performance in this synthetic simulator; they are not evidence about real-world matching outcomes.
Compare the supplied baselines
The starter includes three baseline modes. These are useful reference points before testing policy changes.
```bash
python evaluate.py --baseline greedy --seeds 101,102,103 --variants all --output results/greedy.json
python evaluate.py --baseline no_asks --seeds 101,102,103 --variants all --output results/no_asks.json
python evaluate.py --baseline random --seeds 101,102,103 --variants all --output results/random.json
```
These full runs take longer than the quick-start evaluation. The public scenario variants are `development`, `sparse`, `cold_start`, `delayed`, `shift`, and `drift`.
My preliminary baseline runs
I ran the three baseline modes using seeds `101`, `102`, and `103` across the six public scenario variants. All 18 episodes were valid for each baseline.
Baseline	Primary score (MSMI per 100 arrived members)	Coverage	Mutual acceptances per 100
Greedy	0.389	37.17%	5.50
Random	0.278	37.67%	5.33
No clarification	0.139	14.28%	1.75
These are preliminary results from three seeds per scenario, not statistically conclusive findings. Greedy had the highest primary score in this small run; random had slightly higher coverage. The comparison does not isolate the causal effect of clarification because the matching behavior differs between modes as well.
What I am working on
My focus is understanding the supplied implementation, analysing baseline performance, and experimenting with ways to improve sequential matching. Potential areas include:
scoring feasible pairs more meaningfully;
deciding when clarification could change a matching decision;
comparing local greedy selection with batch-level allocation;
testing changes against the same seeds and scenario variants.
The existence of an idea in this list does not mean it has already been implemented or shown to improve results. I will distinguish starter-project functionality, my own modifications, and experimental findings in any report.
Repository map
File or folder	What it is for
`PROBLEM_STATEMENT.md`	Official challenge description and rules
`data/`	Supplied synthetic data
`data_manifest.json`	Dataset counts, seeds, and splits
`docs/DATA_CONTRACT.md`	Data fields, constraints, and feedback rules
`docs/POLICY_INTERFACE.md`	Required policy input/output protocol
`policy.py`	Policy adapter and baseline modes
`evaluate.py`	Public evaluation harness
`kit.py`	Simulator utilities and eligibility checks
`Dockerfile`	Container packaging for policy evaluation
`docs/SUBMISSION.md`	Official submission instructions
`examples/REPORT_GUIDE.md`	Guide to the final technical report
`LICENSE` and `DATA_LICENSE.md`	Code and synthetic-data reuse terms
For the complete file inventory and authoritative rules, see the official upstream README.
Container check
If Docker is installed, build and test the policy container:
```bash
docker build -t sequential-policy:1.0 .
python evaluate.py --image sequential-policy:1.0 --seeds 101 --output results/container.json
```
The assessed environment is offline. Do not rely on network access or private organiser data from inside the policy.
Data and evaluation notes
Keep training, validation, and development-test pools separate.
Use only information observable at the time a decision is made.
Treat unknown values as unknown; do not silently turn them into negative preferences.
Respect reciprocal hard constraints, clarification budgets, availability, and restrictions on repeat or outstanding introductions.
Report scenario-level results and limitations, not only one aggregate score.
Hackathon context
This is my working repository for model-analysis and policy experiments for the IIT Madras × RomeoJulietLove Hackathon. The official challenge repository remains the source of truth for the problem specification, simulator, data contract, starter implementation, and submission rules.
I have reused the original project as a starting point and credit its author. Any work I claim as my own is limited to the experiments, analysis, documentation, and code changes I actually make. Please consult the upstream repository for the original project and its history.
---
