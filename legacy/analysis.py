"""
FTP Analysis and Training Program Generator

This module provides tools for:
1. Calculating FTP (Functional Threshold Power) progression
2. Identifying training zones (Z1-Z5)
3. Analyzing intensity metrics
4. Generating periodized 6-8 week training programs
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class FTPAnalyzer:
    """Analyze Peloton workout data to track FTP progression and training zones"""
    
    # Standard zone boundaries as % of FTP
    ZONES = {
        'Z1': (0.00, 0.56),      # Active Recovery
        'Z2': (0.56, 0.76),      # Endurance
        'Z3': (0.76, 0.90),      # Tempo
        'Z4': (0.90, 1.05),      # Threshold
        'Z5': (1.05, float('inf')) # VO2 Max / Anaerobic
    }
    
    def __init__(self, metrics_df):
        """
        Initialize analyzer with metrics data
        
        Args:
            metrics_df: DataFrame with columns: created_at, total_output (or similar)
        """
        self.metrics_df = metrics_df.copy()
        self.metrics_df['created_at'] = pd.to_datetime(self.metrics_df['created_at'])
        self.ftp_history = self._calculate_ftp_history()
    
    def _calculate_ftp_history(self):
        """
        Calculate estimated FTP over time using 20-min power test method
        
        Uses rolling 20-minute averages on high-intensity workouts.
        This is a simplified estimate; actual FTP requires formal testing.
        
        Returns:
            DataFrame with date and estimated FTP
        """
        if self.metrics_df.empty:
            return pd.DataFrame()
        
        # Try different possible column names for output/power
        power_cols = ['total_output', 'avg_power', 'output', 'average_output']
        power_col = None
        
        for col in power_cols:
            if col in self.metrics_df.columns:
                power_col = col
                break
        
        if power_col is None:
            print("⚠️  Warning: No power/output column found in metrics")
            return pd.DataFrame()
        
        # Sort by date
        df = self.metrics_df[['created_at', power_col]].copy()
        df = df.sort_values('created_at')
        
        # Remove zero values
        df = df[df[power_col] > 0]
        
        if df.empty:
            return pd.DataFrame()
        
        # Group by week and calculate average output
        df['week'] = df['created_at'].dt.to_period('W')
        weekly_power = df.groupby('week')[power_col].mean()
        
        # FTP estimation: 95% of average power (simplified)
        # Note: This is a rough estimate. Actual FTP requires formal testing.
        ftp_history = pd.DataFrame({
            'date': weekly_power.index.to_timestamp(),
            'estimated_ftp': weekly_power.values * 0.95,
            'avg_weekly_output': weekly_power.values
        })
        
        return ftp_history
    
    def get_ftp_progression(self):
        """Get FTP progression over time"""
        return self.ftp_history
    
    def get_current_ftp(self):
        """Get estimated current FTP"""
        if self.ftp_history.empty:
            return None
        return self.ftp_history.iloc[-1]['estimated_ftp']
    
    def categorize_by_zone(self, estimated_ftp):
        """
        Categorize a power value into a training zone
        
        Args:
            estimated_ftp: Estimated FTP value
            power: Power output value
        
        Returns:
            Zone name (Z1-Z5)
        """
        if estimated_ftp is None or estimated_ftp <= 0:
            return 'Unknown'
        
        # This would categorize individual workouts
        # Usage: analyze individual rides against FTP
        pass
    
    def get_intensity_distribution(self, weeks=12):
        """
        Get distribution of training intensity over recent period
        
        Args:
            weeks: Number of weeks to analyze
        
        Returns:
            DataFrame with zone distribution
        """
        if self.metrics_df.empty:
            return pd.DataFrame()
        
        cutoff_date = datetime.now() - timedelta(weeks=weeks)
        recent_df = self.metrics_df[self.metrics_df['created_at'] >= cutoff_date]
        
        if recent_df.empty:
            return pd.DataFrame({
                'metric': ['Duration', 'Rides'],
                'value': [0, 0]
            })
        
        return pd.DataFrame({
            'metric': ['Total Rides', 'Total Hours', 'Avg Duration (min)'],
            'value': [
                len(recent_df),
                recent_df['workout_duration'].sum() / 60 if 'workout_duration' in recent_df.columns else 0,
                recent_df['workout_duration'].mean() if 'workout_duration' in recent_df.columns else 0
            ]
        })


class TrainingProgramGenerator:
    """Generate periodized 6-8 week training programs based on FTP data"""
    
    def __init__(self, current_ftp, training_level='intermediate'):
        """
        Initialize program generator
        
        Args:
            current_ftp: Current FTP estimate
            training_level: 'beginner', 'intermediate', or 'advanced'
        """
        self.current_ftp = current_ftp
        self.training_level = training_level
        self.program = None
    
    def generate_6_week_build(self, target_ftp_increase=5.0):
        """
        Generate a 6-week FTP-building program
        
        Structure:
        - Week 1-2: Base (Z2-Z3 endurance builds)
        - Week 3-4: Build (threshold and tempo intervals)
        - Week 5: Peak (VO2 max and anaerobic work)
        - Week 6: Recovery/test
        
        Args:
            target_ftp_increase: Target % increase in FTP (default 5%)
        
        Returns:
            DataFrame with weekly workout recommendations
        """
        weeks = []
        
        # Week 1-2: Base Phase
        for week in [1, 2]:
            weeks.append({
                'week': week,
                'phase': 'Base',
                'focus': 'Endurance & Aerobic Capacity',
                'zone_target': 'Z2-Z3',
                'intensity': 'Moderate',
                'weekly_ftp_percentage': 0.75,
                'rides_per_week': 3,
                'avg_duration_min': 45,
                'description': f'Week {week}: Build aerobic base with steady-state rides'
            })
        
        # Week 3-4: Build Phase
        for week in [3, 4]:
            weeks.append({
                'week': week,
                'phase': 'Build',
                'focus': 'Threshold & Tempo',
                'zone_target': 'Z3-Z4',
                'intensity': 'Hard',
                'weekly_ftp_percentage': 0.90,
                'rides_per_week': 3,
                'avg_duration_min': 50,
                'description': f'Week {week}: Tempo and threshold intervals to build sustainable power'
            })
        
        # Week 5: Peak Phase
        weeks.append({
            'week': 5,
            'phase': 'Peak',
            'focus': 'VO2 Max',
            'zone_target': 'Z4-Z5',
            'intensity': 'Very Hard',
            'weekly_ftp_percentage': 1.00,
            'rides_per_week': 3,
            'avg_duration_min': 45,
            'description': 'Week 5: High-intensity intervals to drive VO2 max improvements'
        })
        
        # Week 6: Recovery
        weeks.append({
            'week': 6,
            'phase': 'Recovery/Test',
            'focus': 'Recovery & FTP Test',
            'zone_target': 'Z1-Z2 + Test',
            'intensity': 'Easy + Moderate',
            'weekly_ftp_percentage': 0.70,
            'rides_per_week': 2,
            'avg_duration_min': 40,
            'description': 'Week 6: Recovery rides + FTP test to measure progress'
        })
        
        self.program = pd.DataFrame(weeks)
        return self.program
    
    def generate_8_week_periodized(self, target_ftp_increase=8.0):
        """
        Generate an 8-week periodized FTP-building program
        
        Structure:
        - Week 1-2: Base (low intensity)
        - Week 3-4: Build (threshold work)
        - Week 5-6: Peak (VO2 + anaerobic)
        - Week 7-8: Recovery & test
        
        Args:
            target_ftp_increase: Target % increase in FTP
        
        Returns:
            DataFrame with weekly workout recommendations
        """
        weeks = []
        
        # Week 1-2: Aerobic Base
        for week in [1, 2]:
            weeks.append({
                'week': week,
                'phase': 'Aerobic Base',
                'focus': 'Build fitness foundation',
                'zone_target': 'Z1-Z2',
                'intensity': 'Easy to Moderate',
                'weekly_ftp_percentage': 0.70,
                'rides_per_week': 3,
                'avg_duration_min': 50,
                'description': f'Week {week}: Steady endurance work to build aerobic base'
            })
        
        # Week 3-4: Threshold Build
        for week in [3, 4]:
            weeks.append({
                'week': week,
                'phase': 'Threshold Build',
                'focus': 'Raise FTP ceiling',
                'zone_target': 'Z3-Z4',
                'intensity': 'Hard',
                'weekly_ftp_percentage': 0.85,
                'rides_per_week': 3,
                'avg_duration_min': 50,
                'description': f'Week {week}: Sustained threshold intervals (8-20min efforts)'
            })
        
        # Week 5-6: Peak Power
        for week in [5, 6]:
            weeks.append({
                'week': week,
                'phase': 'Peak Power',
                'focus': 'VO2 Max & Anaerobic',
                'zone_target': 'Z4-Z5',
                'intensity': 'Very Hard',
                'weekly_ftp_percentage': 0.95,
                'rides_per_week': 3,
                'avg_duration_min': 45,
                'description': f'Week {week}: High-intensity intervals (3-8min) to build power'
            })
        
        # Week 7: Taper/Recovery
        weeks.append({
            'week': 7,
            'phase': 'Taper',
            'focus': 'Active Recovery',
            'zone_target': 'Z1-Z2',
            'intensity': 'Easy',
            'weekly_ftp_percentage': 0.65,
            'rides_per_week': 2,
            'avg_duration_min': 35,
            'description': 'Week 7: Recovery rides to allow adaptation'
        })
        
        # Week 8: Test
        weeks.append({
            'week': 8,
            'phase': 'Test/Assess',
            'focus': 'FTP Testing',
            'zone_target': 'Moderate to Hard',
            'intensity': 'Controlled',
            'weekly_ftp_percentage': 0.80,
            'rides_per_week': 2,
            'avg_duration_min': 50,
            'description': 'Week 8: 20-minute FTP test + easy recovery ride'
        })
        
        self.program = pd.DataFrame(weeks)
        return self.program
    
    def export_program(self, output_path):
        """Export training program to CSV"""
        if self.program is not None:
            self.program.to_csv(output_path, index=False)
            print(f"✅ Program exported to {output_path}")
        else:
            print("⚠️  No program generated yet")


def analyze_workouts(metrics_df):
    """
    Quick analysis of workouts
    
    Args:
        metrics_df: DataFrame with workout metrics
    
    Returns:
        Dictionary with summary statistics
    """
    if metrics_df.empty:
        return {}
    
    return {
        'total_workouts': len(metrics_df),
        'avg_duration_min': metrics_df.get('workout_duration', pd.Series()).mean() if 'workout_duration' in metrics_df.columns else 0,
        'total_hours': metrics_df.get('workout_duration', pd.Series()).sum() / 60 if 'workout_duration' in metrics_df.columns else 0,
        'date_range': f"{metrics_df['created_at'].min().date()} to {metrics_df['created_at'].max().date()}" if 'created_at' in metrics_df.columns else 'N/A'
    }
