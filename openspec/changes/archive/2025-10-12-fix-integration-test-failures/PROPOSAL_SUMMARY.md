# OpenSpec Proposal Summary: Fix Integration Test Failures

## Quick Reference

**Proposal ID**: `fix-integration-test-failures`  
**Status**: Draft - Ready for Implementation  
**Priority**: High  
**Estimated Effort**: 7 hours (1.5 working days)  

## The Problem

29 out of 83 tests are failing (35% failure rate) due to:
- REST API context handling issues
- Form submission handlers missing
- Model relationship query errors
- Session management problems

## The Solution

Implement proper context handling, database helpers, and session management through 5 phases:

1. **Context Access Layer** (45 min) - Helper functions
2. **REST API Integration** (2 hrs) - Fix 11 tests
3. **Form Handlers** (1.5 hrs) - Fix 7 tests
4. **Model Relationships** (1 hr) - Fix 6 tests
5. **Session Management** (1 hr) - Fix 5 tests

## Expected Outcome

- ✅ **100% test success rate** (83/83 tests passing)
- ✅ **Improved code maintainability**
- ✅ **Better error handling**
- ✅ **Consistent authorization**

## Key Features

### Helper Functions
```python
get_current_user()  # Safe context access
is_admin()          # Role checking
get_or_404(model, id)  # Safe queries
safe_first(query)   # No AttributeError
```

### REST API Improvements
- Automatic user association
- Permission checks (ownership + admin)
- Proper error responses (401, 403, 404, 422)

### Form Handling
- POST handlers for all forms
- Validation with error messages
- Redirect after successful submission
- CSRF protection

### Test Infrastructure
- Persistent session in `logged_client`
- Helper functions for common assertions
- Better fixture organization

## Implementation Plan

### Phase 1: Helpers (45 min)
→ Foundation for all other phases

### Phase 2: REST API (2 hrs)
→ Fixes: 11 tests (78% passing)

### Phase 3: Forms (1.5 hrs)
→ Fixes: 7 tests (87% passing)

### Phase 4: Models (1 hr)
→ Fixes: 6 tests (94% passing)

### Phase 5: Sessions (1 hr)
→ Fixes: 5 tests (100% passing) ✅

## Files to Modify

| File | Changes | Impact |
|------|---------|--------|
| `runtime/app.py` | +150 lines | Medium |
| `runtime/tests.py` | +50 lines | Low |
| `documentation/` | Updates | None |

## Risk Level

**Overall Risk**: Low

- ✅ No breaking API changes
- ✅ Incremental implementation
- ✅ Each phase independently testable
- ✅ Easy rollback per phase

## Success Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Tests Passing | 54/83 (65%) | 83/83 (100%) | +35% |
| Core Tests | 33/33 ✅ | 33/33 ✅ | Maintained |
| Integration Tests | 21/50 | 50/50 ✅ | +29 tests |
| Test Coverage | ~80% | ~90% | +10% |

## Timeline

**Start**: When approved  
**Phase 1**: Day 1 Morning  
**Phase 2**: Day 1 Afternoon  
**Phase 3**: Day 2 Morning  
**Phase 4**: Day 2 Midday  
**Phase 5**: Day 2 Afternoon  
**Complete**: End of Day 2

## Next Steps

1. ✅ Review proposal
2. ✅ Approve design
3. ⏳ Begin Phase 1 implementation
4. ⏳ Test after each phase
5. ⏳ Document final results

## Related Documents

- 📄 **Full Proposal**: `proposal.md`
- 🏗️ **Design Document**: `design.md`
- ✅ **Task Breakdown**: `tasks.md`
- 📊 **Current Status**: `../../documentation/TEST_FIX_SUMMARY.md`

## Quick Start

To begin implementation:

```bash
# 1. Review the proposal
cat openspec/changes/fix-integration-test-failures/proposal.md

# 2. Review the design
cat openspec/changes/fix-integration-test-failures/design.md

# 3. Start with Phase 1, Task 1.1
# See tasks.md for detailed steps

# 4. Test continuously
pytest tests.py --no-cov -v
```

## Contact

For questions about this proposal:
- Review design document for technical details
- Check tasks.md for implementation specifics
- See test output in TEST_FIX_SUMMARY.md

---

**Status**: Ready for implementation  
**Approval**: Pending  
**Implementation**: Can start immediately

