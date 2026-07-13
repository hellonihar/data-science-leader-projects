# Run database migrations and seed data
# Usage: .\scripts\migrate.ps1

Write-Host "Running database migrations..." -ForegroundColor Cyan
uv run alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migrations complete. Seeding data..." -ForegroundColor Cyan
    uv run python -m app.seed
}

Write-Host "Done!" -ForegroundColor Green
