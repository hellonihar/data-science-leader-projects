# Reset database: drop all tables, re-run migrations, and re-seed
# Usage: .\scripts\reset_db.ps1

Write-Host "Dropping all tables..." -ForegroundColor Yellow
uv run alembic downgrade base

Write-Host "Re-running migrations..." -ForegroundColor Cyan
uv run alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "Re-seeding data..." -ForegroundColor Cyan
    uv run python -m app.seed
}

Write-Host "Database reset complete!" -ForegroundColor Green
