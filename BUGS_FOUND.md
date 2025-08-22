# Bugs and Issues Found During Testing

**Report Date**: January 6, 2025  
**Testing Phase**: Comprehensive testing execution  
**Test Environment**: Python 3.12.3, pytest 8.4.1

## Critical Issues

### BUG-001: Database Schema Issues in Tests
**Severity**: Critical  
**Priority**: P1  
**Component**: Models/Database  
**Status**: In Progress - Partially Fixed

**Description**: 
Multiple test failures due to SQLAlchemy OperationalError: "(sqlite3.OperationalError) no such table: portfolios"

**Error Details**:
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: portfolios
[SQL: SELECT portfolios.id AS portfolios_id, portfolios.name AS portfolios_name, portfolios.created_date AS portfolios_created_date, portfolios.modified_date AS portfolios_modified_date 
FROM portfolios]
```

**Affected Tests**:
- test_portfolios_list_empty
- test_create_portfolio_success  
- test_create_duplicate_portfolio
- test_portfolio_detail_not_found
- test_api_portfolios_empty

**Root Cause**: 
Database tables are not being created properly in test environment. The test database setup is not executing the table creation correctly.

**Impact**: 
Tests cannot run properly, blocking verification of core portfolio functionality.

---

## High Priority Issues

### BUG-002: Pydantic V1 Style Validators Deprecated
**Severity**: High  
**Priority**: P2  
**Component**: Controllers  
**Status**: Fixed

**Description**: 
Multiple deprecation warnings for Pydantic V1 style `@validator` decorators that will be removed in Pydantic V3.0.

**Affected Files**:
- `controllers/portfolio_controller.py:59`
- `controllers/watchlist_controller.py:14, 25, 37, 43, 54`

**Error Message**:
```
PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. 
You should migrate to Pydantic V2 style `@field_validator` validators
```

**Impact**: 
Code will break when Pydantic V3.0 is released. Warnings clutter test output.

---

### BUG-003: FastAPI on_event Deprecation
**Severity**: High  
**Priority**: P2  
**Component**: Web Server  
**Status**: Fixed

**Description**: 
FastAPI `on_event` decorator is deprecated in favor of lifespan event handlers.

**Affected Files**:
- `web_server/app.py:63`

**Error Message**:
```
DeprecationWarning: on_event is deprecated, use lifespan event handlers instead.
```

**Impact**: 
Application startup/shutdown events may not work in future FastAPI versions.

---

### BUG-004: Starlette TemplateResponse Parameter Order
**Severity**: High  
**Priority**: P2  
**Component**: Web Server/Templates  
**Status**: Identified

**Description**: 
Starlette TemplateResponse parameter order is deprecated. Request should be first parameter.

**Affected Areas**: Multiple template responses

**Error Message**:
```
DeprecationWarning: The `name` is not the first parameter anymore. 
The first parameter should be the `Request` instance.
Replace `TemplateResponse(name, {"request": request})` by `TemplateResponse(request, name)`.
```

**Impact**: 
Template rendering may break in future Starlette versions.

---

## Medium Priority Issues

### BUG-005: datetime.utcnow() Deprecation
**Severity**: Medium  
**Priority**: P3  
**Component**: Models/Database  
**Status**: Fixed

**Description**: 
`datetime.datetime.utcnow()` is deprecated and scheduled for removal.

**Error Message**:
```
DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. 
Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
```

**Impact**: 
Timestamp creation will break in future Python versions.

---

## Test Coverage Analysis

### Current Test Results
- **Total Tests**: 24
- **Passed**: 19 (79.2%)
- **Failed**: 5 (20.8%)
- **Warnings**: 43

### Test Categories Status
- ✅ **CSV Parser Tests**: All passing (4/4)
- ✅ **Holdings API Tests**: All passing (4/4)  
- ✅ **Web Form Tests**: All passing (3/3)
- ❌ **Basic Portfolio Tests**: 5/9 failing due to database issues
- ⚠️  **Deprecation Warnings**: 43 warnings need addressing

### Missing Test Coverage
Based on the test plan, we still need:
- Watchlist controller tests
- News controller tests  
- Stock data controller tests
- Rebalancing controller tests
- Integration tests for external APIs
- Performance tests
- Security tests

## Bug Priority Classification

### P1 (Critical - Fix Immediately)
- ❌ BUG-001: Database schema issues (In Progress)

### P2 (High - Fix Before Release)  
- ✅ BUG-002: Pydantic validator deprecation (Fixed)
- ✅ BUG-003: FastAPI on_event deprecation (Fixed)
- ❌ BUG-004: TemplateResponse parameter order (Pending)

### P3 (Medium - Fix In Next Sprint)
- ✅ BUG-005: datetime.utcnow() deprecation (Fixed)

## Fix Progress Summary

**Completed Fixes (4/5):**
1. ✅ **BUG-002**: Updated all Pydantic validators from V1 `@validator` to V2 `@field_validator` style
   - Files fixed: `controllers/portfolio_controller.py`, `controllers/watchlist_controller.py`, `utils/csv_parser.py`
   - All validators now use `@field_validator` with `@classmethod` decorator

2. ✅ **BUG-003**: Migrated FastAPI from deprecated `on_event` to modern `lifespan` function
   - File fixed: `web_server/app.py`
   - Added `@asynccontextmanager` lifespan function for startup/shutdown events

3. ✅ **BUG-005**: Replaced deprecated `datetime.utcnow()` with timezone-aware `datetime.now(timezone.utc)`
   - Files fixed: `models/portfolio.py`, `controllers/news_controller.py`, `web_server/routes/watchlists.py`
   - Added helper function `utc_now()` for consistent timezone handling

**In Progress (1/5):**
4. ❌ **BUG-001**: Database schema issues in tests - Added conftest.py but still troubleshooting fixture setup

**Pending (1/5):**
5. ❌ **BUG-004**: TemplateResponse parameter order - Need to update template responses

## Next Steps

1. **Immediate Actions**:
   - Fix database table creation in tests (BUG-001)
   - Upgrade Pydantic validators to V2 style (BUG-002)
   - Migrate to FastAPI lifespan events (BUG-003)
   - Fix TemplateResponse parameter order (BUG-004)

2. **Testing Expansion**:
   - Add comprehensive controller tests
   - Add integration tests
   - Add error handling tests
   - Add performance tests

3. **Code Quality**:
   - Fix all deprecation warnings
   - Improve test coverage to >90%
   - Add type hints where missing
   - Update to modern Python/FastAPI patterns

## Test Environment Notes

- Python 3.12.3 detected several deprecations that weren't visible in older versions
- SQLite in-memory database has different behavior than file-based database
- FastAPI TestClient has some limitations with async operations
- Need to add proper test database isolation

---

**Last Updated**: January 6, 2025  
**Next Review**: After bug fixes are implemented