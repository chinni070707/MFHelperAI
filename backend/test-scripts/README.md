# Test Scripts for CAS Parsing Development

This folder contains test scripts used during CAS parsing feature development. These are **not** production code and are kept for reference and debugging.

## 📁 Test Categories

### CAS Format Testing
- `check_cas_format.py` - Checks CAS PDF format type
- `debug_file_type.py` - Debug file type detection
- `test_regex_pattern.py` - Tests regex patterns for parsing

### casparser Library Testing
- `test_casparser_library.py` - Basic casparser library test
- `test_casparser_backends.py` - Tests different parsing backends (mupdf, pdfminer)
- `test_cas_parser.py` - General CAS parsing tests
- `test_cas_direct.py` - Direct PDF text extraction
- `test_cas_import.py` - Tests CAS import with casparser
- `test_cas_final.py` - Comprehensive CAS parsing test
- `test_cas_robust.py` - Robust parsing with error handling

### Format-Specific Tests
- `test_kfintech_cas.py` - **SUCCESSFUL** KFintech CAS test with real file
- `test_nsdl_parser_direct.py` - NSDL/CDSL format testing

### API Endpoint Testing
- `test_cas_upload_endpoint.py` - Tests `/api/upload/cas` endpoint

## ✅ Production Code

The actual production code is in:
- `backend/app/routes/cas.py` - CAS upload API endpoint
- `backend/app/services/cas_import.py` - Database import service

## 🎯 Main Scripts (Not Tests)

Production scripts in `backend/scripts/`:
- `seed_database.py` - Populate database with test data
- `quick_seed.py` - Quick database seeding
- `generate_user_holdings.py` - Generate sample holdings
- `load_holdings_to_db.py` - Load holdings to database
- `weekly_update.py` - Weekly maintenance tasks

## 📝 Usage

These test scripts require:
```bash
pip install casparser[fast]
```

To run a test:
```bash
cd backend/test-scripts
python test_kfintech_cas.py
```

**Note**: Update file paths and passwords in scripts before running.

## 🗑️ Cleanup

These scripts can be safely deleted once the CAS import feature is stable and well-tested in production. They're kept for:
- Reference during debugging
- Understanding casparser behavior
- Testing new CAS formats
- Development history
