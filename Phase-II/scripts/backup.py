#!/usr/bin/env python3
"""
Backup script for the Todo Application Backend.
This script handles database backups and other maintenance tasks.
"""

import os
import sys
import subprocess
import datetime
import shutil
from pathlib import Path
from typing import Optional
import argparse
import logging
from contextlib import contextmanager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackupManager:
    """
    Manager class for handling backups of the Todo Application.
    """

    def __init__(self, backup_dir: str = "./backups", retention_days: int = 7):
        """
        Initialize the backup manager.

        Args:
            backup_dir: Directory to store backups
            retention_days: Number of days to retain backups
        """
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days

        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_database_backup(self, db_url: Optional[str] = None) -> Optional[Path]:
        """
        Create a backup of the database.

        Args:
            db_url: Database URL to backup (if None, uses environment variable)

        Returns:
            Path to the backup file or None if failed
        """
        if not db_url:
            db_url = os.getenv("NEON_DB_URL")

        if not db_url:
            logger.error("No database URL provided and NEON_DB_URL environment variable not set")
            return None

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"todo_app_backup_{timestamp}.sql"
        backup_path = self.backup_dir / backup_filename

        try:
            # For PostgreSQL, use pg_dump
            if "postgresql" in db_url.lower() or "postgres" in db_url.lower():
                # Extract connection parameters from URL
                import re
                match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
                if not match:
                    logger.error("Could not parse PostgreSQL URL")
                    return None

                username, password, host, port, dbname = match.groups()

                # Use environment variables for password to avoid command line exposure
                env = os.environ.copy()
                env['PGPASSWORD'] = password

                cmd = [
                    'pg_dump',
                    '-h', host,
                    '-p', port,
                    '-U', username,
                    '-d', dbname,
                    '-f', str(backup_path)
                ]

                result = subprocess.run(cmd, env=env, capture_output=True, text=True)

                if result.returncode != 0:
                    logger.error(f"pg_dump failed: {result.stderr}")
                    return None

                logger.info(f"Database backup created: {backup_path}")
                return backup_path
            else:
                logger.error(f"Unsupported database type in URL: {db_url}")
                return None

        except Exception as e:
            logger.error(f"Error creating database backup: {str(e)}")
            return None

    def cleanup_old_backups(self):
        """
        Remove backup files older than the retention period.
        """
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.retention_days)

        for backup_file in self.backup_dir.glob("todo_app_backup_*.sql"):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                try:
                    backup_file.unlink()
                    logger.info(f"Removed old backup: {backup_file}")
                except Exception as e:
                    logger.error(f"Error removing old backup {backup_file}: {str(e)}")

    def run_backup(self) -> bool:
        """
        Run a complete backup operation.

        Returns:
            bool: True if backup was successful, False otherwise
        """
        logger.info("Starting backup process...")

        # Create database backup
        db_backup = self.create_database_backup()
        if not db_backup:
            logger.error("Database backup failed")
            return False

        # Cleanup old backups
        self.cleanup_old_backups()

        logger.info("Backup process completed successfully")
        return True


def main():
    """
    Main function to run the backup script.
    """
    parser = argparse.ArgumentParser(description='Todo Application Backup Script')
    parser.add_argument('--backup-dir', default='./backups', help='Directory to store backups')
    parser.add_argument('--retention-days', type=int, default=7, help='Number of days to retain backups')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without doing it')
    parser.add_argument('--db-url', help='Database URL to backup (overrides environment variable)')

    args = parser.parse_args()

    # Validate arguments
    if args.retention_days < 1:
        logger.error("Retention days must be at least 1")
        sys.exit(1)

    if args.dry_run:
        logger.info("DRY RUN: Would create backup in directory: %s", args.backup_dir)
        logger.info("DRY RUN: Would retain backups for %d days", args.retention_days)
        if args.db_url:
            logger.info("DRY RUN: Would backup database: %s", args.db_url)
        else:
            logger.info("DRY RUN: Would backup database from NEON_DB_URL environment variable")
        return 0

    # Create backup manager
    backup_manager = BackupManager(
        backup_dir=args.backup_dir,
        retention_days=args.retention_days
    )

    # Run backup
    success = backup_manager.run_backup()

    if success:
        logger.info("Backup completed successfully")
        return 0
    else:
        logger.error("Backup failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())