# Scientific programming | Automated quality checks

## Objective
Build a Python demonstration that checks the consistency and completeness of structured scientific-computing records.

## Implementation
The included software uses synthetic Vina-style ZIP fixtures to exercise parsers and checks for log entries, pose scores, execution configuration, required files and summary consistency. A baseline and updated checker can be compared using fault-injection cases.

## Demonstrated skill
Python scripting, test fixtures, fault injection, regression checks, structured exception reporting, and the distinction between **record consistency** and **scientific correctness**.

## Reproduce
See the [QA auditor README](../qa_auditor/README.md). The demonstration uses Python 3.9+ and the standard library. It does not execute docking software or access restricted research data.
