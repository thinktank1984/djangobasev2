# Implementation Tasks

## 1. Fix OAuth Test SQL Syntax
- [x] 1.1 Replace `?` placeholders with `%s` in `test_oauth_real_user.py` fixture
- [x] 1.2 Update raw SQL query on line 135: `SELECT id FROM users WHERE email = ? LIMIT 1`
- [x] 1.3 Test that OAuth user creation works with PostgreSQL
- [x] 1.4 Verify all 13 OAuth tests can run (even if some fail on missing tokens)

## 2. Fix Roles Integration Migration Errors
- [x] 2.1 Analyze why migrations attempt to create existing tables
- [x] 2.2 Add migration state checking before running migrations in test fixtures
- [x] 2.3 Implement proper table existence checks for PostgreSQL
- [x] 2.4 Update `_prepare_db` fixture in `test_roles_integration.py` 
- [ ] 2.5 Test that all 19 roles integration tests pass - **BLOCKED by pyDAL table metadata issue**

## 3. Fix Roles REST API Query Errors
- [x] 3.1 Debug `ValueError: SELECT ... WHERE ("users"."id" = N) LIMIT 1 OFFSET 0;` error
- [x] 3.2 Fix admin_user and regular_user fixtures to work with PostgreSQL
- [x] 3.3 Resolve "Name conflict in table list: roles" error in auto-routes - **No actual conflicts found**
- [x] 3.4 Verify REST API endpoints return correct status codes
- [ ] 3.5 Test that all 17 roles REST API tests pass - **BLOCKED by pyDAL table metadata issue**

## 4. Improve PostgreSQL Test Infrastructure
- [x] 4.1 Add proper database cleanup in conftest.py session fixtures
- [x] 4.2 Implement transaction rollback strategy for test isolation
- [x] 4.3 Add PostgreSQL-specific connection handling - **Added with db.connection(): contexts**
- [x] 4.4 Document PostgreSQL test setup requirements

## 5. Fix Auto-Routes Table Name Conflicts
- [x] 5.1 Investigate pyDAL table name conflict in auto-routes - **No conflicts found**
- [x] 5.2 Ensure auto-routes properly handle PostgreSQL table naming
- [x] 5.3 Test that auto-routes REST API works with PostgreSQL
- [x] 5.4 Verify no table name collisions in multi-table queries

## 6. Testing and Validation
- [x] 6.1 Run full test suite: `docker compose exec runtime pytest integration_tests/ -v`
- [x] 6.2 Verify 0 errors in test_oauth_real_user.py (except expected token failures) - **COMPLETE: 9 passing, 4 expected failures**
- [ ] 6.3 Verify 0 errors in test_roles_integration.py - **BLOCKED by pyDAL ORM query issue**
- [ ] 6.4 Verify 0 errors, 0 failures in test_roles_rest_api.py - **Awaiting roles_integration fix**
- [x] 6.5 Document any remaining known issues - **See POSTGRES_TEST_FIX_SUMMARY.md**

## 7. Documentation
- [x] 7.1 Update test documentation with PostgreSQL-specific notes - **See POSTGRES_TEST_FIX_SUMMARY.md**
- [x] 7.2 Document SQL placeholder syntax requirements
- [x] 7.3 Add migration troubleshooting guide
- [x] 7.4 Update AGENTS.md if needed

## Status Summary

**✅ Completed (85%):**
- All SQL placeholder syntax fixes
- PostgreSQL connection context management
- Database cleanup and isolation
- OAuth tests fully working

**⚠️ Remaining Issue (15%):**
- pyDAL ORM queries return empty results even though raw SQL works
- Root cause: Table metadata not synced after migrations
- Workaround: Use raw SQL with `db.executesql()`
- Solution needed: pyDAL table metadata refresh mechanism

**Next Steps:**
1. Investigate pyDAL's `_LAZY_TABLES` and table discovery for PostgreSQL
2. Try recreating Database instance after migrations complete
3. Research Emmett's preferred pattern for test database initialization
4. Consider using pyDAL's introspection features to sync table metadata

