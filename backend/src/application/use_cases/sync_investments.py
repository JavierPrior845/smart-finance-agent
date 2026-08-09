import uuid
from datetime import datetime, timedelta, date, timezone
from typing import List
import asyncio
import yfinance as yf

from src.application.ports.investment_repository import InvestmentRepository
from src.domain.models.investment import InvestmentSnapshot

class SyncInvestmentsUseCase:
    def __init__(self, repository: InvestmentRepository):
        self.repository = repository

    async def execute(self) -> None:
        """
        Fetches active assets, determines missing dates up to today, 
        and pulls historical prices from yfinance to fill the gaps.
        """
        active_assets = await self.repository.get_active_assets()
        if not active_assets:
            return

        today = datetime.now(timezone.utc).date()
        snapshots_to_save: List[InvestmentSnapshot] = []

        # We can optimize by fetching all tickers at once, but for simplicity
        # and handling individual gaps, we'll process them asset by asset.
        for asset in active_assets:
            if not asset.ticker:
                continue
                
            last_snapshot_date = await self.repository.get_latest_snapshot_date(asset.id)
            
            # Determine start date
            start_date = None
            if last_snapshot_date:
                # If we have a snapshot from today, skip
                if last_snapshot_date >= today:
                    continue
                start_date = last_snapshot_date + timedelta(days=1)
            else:
                start_date = asset.entry_date.date()
                
            if start_date > today:
                continue
                
            # Fetch data from yfinance. We use start and end date.
            # yfinance expects end date to be exclusive, so we add 1 day to today.
            end_date_yf = today + timedelta(days=1)
            
            try:
                # Run the blocking yfinance call in a thread pool
                loop = asyncio.get_running_loop()
                ticker = yf.Ticker(asset.ticker)
                
                # Use history with start and end
                hist = await loop.run_in_executor(
                    None, 
                    lambda: ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date_yf.strftime("%Y-%m-%d"))
                )
                
                if hist.empty:
                    continue
                    
                # Generate snapshots for the returned days
                for date_idx, row in hist.iterrows():
                    current_date = date_idx.date()
                    price = float(row['Close'])
                    units = asset.units_qty or 0.0
                    
                    snapshot = InvestmentSnapshot(
                        id=uuid.uuid4(),
                        asset_id=asset.id,
                        snapshot_date=current_date,
                        price=price,
                        total_value=price * units,
                        created_at=datetime.now(timezone.utc)
                    )
                    snapshots_to_save.append(snapshot)
                    
            except Exception as e:
                print(f"Error syncing ticker {asset.ticker}: {e}")
                continue
                
        if snapshots_to_save:
            await self.repository.save_snapshots_bulk(snapshots_to_save)
