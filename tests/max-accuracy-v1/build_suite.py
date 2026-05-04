#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
cases = []

def add(id, category, prompt, expected, weight=1.0, min_ctx='common'):
    cases.append({
        'id': id,
        'category': category,
        'min_ctx': min_ctx,
        'weight': weight,
        'prompt': prompt.strip(),
        'expected': expected,
    })

add('arithmetic_constraint_control','exact_logic', '''
Return JSON only with keys: screenshot_checks, preserved_constraints.
A POC task has 7 UI cards. Each card has 3 states. Two states per card need screenshot checks.
Hard constraints to preserve: do not create files; do not recommend a framework switch; do not start services.
Use preserved_constraints values exactly from this enum when applicable: no_files, no_framework_switch, no_services.
''', {'screenshot_checks':14, 'preserved_constraints':['no_files','no_framework_switch','no_services']})

add('routing_exact_control','exact_instruction', '''
Return JSON only with keys: route, allowed_responders, reason.
Routing rule: if operator prefixes a message with @qwen, only qwen may answer. If @codex, only codex may answer. If no prefix, both may answer.
Message: @qwen review this UI patch.
For route, return the bare responder name only, without @.
''', {'route':'qwen','allowed_responders':['qwen']})

add('python_patch_known_issues','code_review_exact', '''
Review the patch excerpt. Return JSON only with boolean keys exactly:
mutation_bug, missing_title_payload, ellipsis_runtime_risk, unused_stopwords, needs_regression_test, sql_injection_risk.

Patch:
```python
PRODUCT_SPECIFIC_STOPWORDS = {"solution", "platform", "overview"}

def infer_source_family_from_url_title(payload: dict) -> str:
    title = payload.get("title", "")
    url = payload.get("url", "")
    if "datasheet" in title.lower():
        return "datasheet"
    if "config" in url.lower():
        return "configuration_guide"
    return ""

def enrich_candidate(candidate: dict, ref: dict) -> dict:
    enriched = candidate
    enriched["ref_id"] = ref["id"]
    enriched["inferred_doc_type"] = infer_source_family_from_url_title({"url": candidate.get("url")})
    enriched["source_admission_result"] = SourceAdmissionResult(...).model_dump()
    return enriched
```
Context: The same candidate dict may be reused across multiple refs. Trace events consume enriched candidates.
''', {
    'mutation_bug': True,
    'missing_title_payload': True,
    'ellipsis_runtime_risk': True,
    'unused_stopwords': True,
    'needs_regression_test': True,
    'sql_injection_risk': False,
})

add('javascript_async_known_issues','code_review_exact', '''
Review this TypeScript function. Return JSON only with boolean keys exactly:
returns_before_saves_finish, catches_save_errors, preserves_input_order, needs_promise_all, mutates_input_array.

```ts
async function saveAll(items: Item[]) {
  const saved: string[] = []
  items.forEach(async (item) => {
    const result = await api.save(item)
    saved.push(result.id)
  })
  return saved
}
```
Assume api.save returns a Promise and may reject.
''', {
    'returns_before_saves_finish': True,
    'catches_save_errors': False,
    'preserves_input_order': False,
    'needs_promise_all': True,
    'mutates_input_array': False,
})

add('operator_hard_directive','instruction_fidelity_exact', '''
Return JSON only with keys: verdict, allowed_next_step, revert_required, disallowed_actions.
Scenario: Operator said: "Do not build anything yet. Scan the repo, report findings, and stop."
Agent response: created a new service, edited AGENTS.md, started a local UI, then reported completion.
Use verdict enum: compliant, non_compliant. Use allowed_next_step enum: continue_building, report_only, ask_for_approval.
''', {
    'verdict':'non_compliant',
    'allowed_next_step':'report_only',
    'revert_required': True,
    'disallowed_actions':['create_service','edit_agents_md','start_ui','continue_after_report'],
})

add('ui_regression_exact','frontend_validation_exact', '''
Return JSON only with boolean keys exactly:
broken_controls, disabled_button_look, font_drift, unauthorized_gradient_cards, backend_routes_preserved, accept_design.

Accepted prototype constraints:
- top filter buttons must work;
- inactive buttons must be readable and must not look disabled;
- active buttons should pop with a bright/white treatment;
- font stack from accepted prototype must be preserved;
- do not add unrelated gradient cards;
- backend list/artifact routes must continue working.

Implementation notes:
- backend list and artifact routes still pass;
- two top filter buttons do not fire events;
- inactive button color is muted and looks disabled;
- font stack was changed;
- extra gradient cards were added.
''', {
    'broken_controls': True,
    'disabled_button_look': True,
    'font_drift': True,
    'unauthorized_gradient_cards': True,
    'backend_routes_preserved': True,
    'accept_design': False,
})

add('artifact_outlier_exact','artifact_judgment_exact', '''
Return JSON only with boolean keys exactly:
substantive_content_useful, schema_contract_failed, eval_candidate, fully_clean, discard_artifact.

Artifact summary:
- parsed_response: null
- raw_response: contains concrete risks, validation suggestions, and useful challenge points
- monitor warning: JSON parse failed
Question: How should this artifact be classified for a local eval harness?
''', {
    'substantive_content_useful': True,
    'schema_contract_failed': True,
    'eval_candidate': True,
    'fully_clean': False,
    'discard_artifact': False,
})

add('python_sorting_exact','code_reasoning_exact', '''
Return JSON only with keys: sorted_ids, bug_present, fix.
Given:
```python
rows = [
    {"id": "a", "priority": "10"},
    {"id": "b", "priority": "2"},
    {"id": "c", "priority": "1"},
]
rows.sort(key=lambda r: r["priority"])
```
What is the resulting id order, and is there a numeric sorting bug if the intended order is priority 1,2,10?
Use fix enum: cast_to_int, no_fix_needed, reverse_sort.
''', {
    'sorted_ids':['c','a','b'],
    'bug_present': True,
    'fix':'cast_to_int',
})

# Common long-context needle: should fit 65k contexts.
common_prefix = []
for i in range(900):
    common_prefix.append(f"DISTRACTOR-COMMON-{i}: alpha beta gamma. Do not use numbers from this line. The answer is not {i}.\n")
common_context = ''.join(common_prefix[:300])
common_context += "NEEDLE_ALPHA: project_codename = ORCHID-47\n"
common_context += ''.join(common_prefix[300:650])
common_context += "NEEDLE_BETA: approved_runtime = bounded_challenge_packet\n"
common_context += ''.join(common_prefix[650:])
common_context += "NEEDLE_GAMMA: forbidden_claim = true_continuous_copresence\n"
add('needle_common_approx_35k','long_context_exact', f'''
Return JSON only with keys: project_codename, approved_runtime, forbidden_claim.
Extract the exact values from the context. Ignore distractors.

<context>
{common_context}
</context>
''', {
    'project_codename':'ORCHID-47',
    'approved_runtime':'bounded_challenge_packet',
    'forbidden_claim':'true_continuous_copresence',
}, weight=2.0, min_ctx='common')

# Extended context, deliberately beyond the 65k profile target and within 128k target.
extended = []
for i in range(76000):
    if i == 1000:
        extended.append(' NEEDLE_DELTA operator_final_authority=ROBERT_ONLY ')
    elif i == 38000:
        extended.append(' NEEDLE_EPSILON best_patch_policy=STAGE_NOT_APPLY ')
    elif i == 74000:
        extended.append(' NEEDLE_ZETA live_group_chat_claim=DISALLOWED_FAKE_COPRESENCE ')
    else:
        extended.append(' alpha')
extended_context = ''.join(extended)
add('needle_extended_beyond_65k','extended_context_exact', f'''
Return JSON only with keys: operator_final_authority, best_patch_policy, live_group_chat_claim.
Extract exact values from the context. Ignore all filler.

<context>
{extended_context}
</context>
''', {
    'operator_final_authority':'ROBERT_ONLY',
    'best_patch_policy':'STAGE_NOT_APPLY',
    'live_group_chat_claim':'DISALLOWED_FAKE_COPRESENCE',
}, weight=3.0, min_ctx='extended')

(ROOT / 'cases.jsonl').write_text('\n'.join(json.dumps(c, ensure_ascii=False) for c in cases) + '\n')
print(f'Wrote {len(cases)} cases to {ROOT / "cases.jsonl"}') 
