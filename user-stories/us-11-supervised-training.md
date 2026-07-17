# US 11 Supervised Fine-Tuning from Annotated Trainer Exports

As a *model maintainer*, I want to *feed a human reviewer's corrections back into the model*, so that *linking mistakes unsupervised training couldn't fix get corrected using real, checked answers*.

"Supervised" here means: someone has told MedCAT the right answer, and now the model updates based on that.

`CAT.train_supervised_from_json` and `CAT.train_supervised_raw` (`medcat/cat.py:803,841`) read a JSON file exported from MedCATtrainer, a tool where a human reviews MedCAT's annotations. Each annotation in that file is marked as correct, incorrect, or reassigned to a different concept. MedCAT uses these marks to strengthen the context vectors for correct links, and weaken the ones for incorrect links.

Here's a risk worth knowing about: a reviewer's correction could accidentally reinforce the same mistake somewhere else. To guard against this, annotations marked `irrelevant` are collected separately, per project (`get_all_irrelevant_cuis`, `medcat/utils/filters.py`), specifically to mark concepts the model should stop suggesting in that particular context. For long training runs, MedCAT can save its progress partway through with `medcat/utils/checkpoint.py` (`Checkpoint.save` / `restore_latest_cdb`), so that a crash partway through a large export doesn't throw away the corrections already applied.

## Acceptance Criteria

1. Given an annotation marked correct
   - when supervised training runs
     - then the existing link between that name and concept is reinforced
2. Given an annotation marked incorrect, or reassigned to a different concept
   - when supervised training runs
     - then the model is adjusted away from the wrong link
3. Given a long training run gets interrupted
   - when it is restarted
     - then it picks up from the last saved checkpoint instead of starting over
4. Given a project exported from the MedCATtrainer web app
   - when it is passed to `train_supervised_from_json`
     - then each annotation's concept code, text span, and correctness flag are used directly, with no reformatting needed

## Case handling (reinforce, penalise, or flag as a guard)

Each annotation is handled according to its correctness flag: "correct" reinforces the link, "incorrect" or "reassigned" penalises it, and "irrelevant" gets added to a per-project guard list. This closes the loop with [MedCATtrainer](https://github.com/CogStack/MedCATtrainer): a reviewer corrects MedCAT's output there, exports it as JSON, and that same file gets fed straight back in. Tests for this live in `tests/test_entity_linking.py`.

## Later stages (deferred)

- **No check for "catastrophic forgetting."** There's currently no automatic safeguard confirming that a supervised training pass doesn't accidentally break previously-correct links; a before-and-after regression check (US 21) could be added.
- **No help choosing what to review.** Reviewers currently pick what to correct entirely by hand. Surfacing the model's least-confident links could help focus review effort where it matters most.
