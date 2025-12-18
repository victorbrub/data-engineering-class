"""
DATA QUALITY ASSESSMENT SCRIPT
==============================

Purpose: Comprehensive data quality analysis across all 6 dimensions
         (Accuracy, Completeness, Consistency, Validity, Uniqueness, Timeliness)

Author: Data Engineering Team
Date: 2024
"""

import pandas as pd
import numpy as np
import requests
import io
from datetime import datetime, timedelta
import re
from collections import Counter
import json
from pathlib import Path

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ============================================================================
# DATA QUALITY ASSESSMENT CLASS
# ============================================================================

class DataQualityAssessment:
    """
    Comprehensive data quality assessment across 6 dimensions
    """
    
    def __init__(self, df, name="Dataset"):
        """
        Initialize the assessment
        
        Parameters:
        -----------
        df : pandas.DataFrame
            The dataset to assess
        name : str
            Name of the dataset
        """
        self.df = df
        self.name = name
        self.assessment_results = {}
        self.timestamp = datetime.now()
        
        print(f"\n{Colors.HEADER}{'='*80}{Colors.RESET}")
        print(f"{Colors.HEADER}DATA QUALITY ASSESSMENT: {name.upper()}{Colors.RESET}")
        print(f"{Colors.HEADER}{'='*80}{Colors.RESET}")
        print(f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Rows: {len(df):,} | Columns: {len(df.columns)}")
        print(f"{Colors.HEADER}{'='*80}{Colors.RESET}\n")
    
    # ========================================================================
    # DIMENSION 1: COMPLETENESS
    # ========================================================================
    
    def assess_completeness(self):
        """
        Assess COMPLETENESS dimension
        - Missing values
        - Null count
        - Completeness percentage
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}DIMENSION 1: COMPLETENESS{Colors.RESET}")
        print(f"{Colors.BLUE}{'-'*80}{Colors.RESET}")
        print("Definition: All required data is present; no missing values\n")
        
        missing_data = {}
        total_cells = len(self.df) * len(self.df.columns)
        total_missing = self.df.isnull().sum().sum()
        
        print(f"{'Column':<20} {'Missing':<15} {'Count':<15} {'Percentage':<15}")
        print("-" * 65)
        
        for column in self.df.columns:
            missing_count = self.df[column].isnull().sum()
            missing_pct = (missing_count / len(self.df)) * 100
            missing_data[column] = {
                'count': missing_count,
                'percentage': missing_pct
            }
            
            if missing_count > 0:
                status = f"{Colors.RED}✗{Colors.RESET}"
            else:
                status = f"{Colors.GREEN}✓{Colors.RESET}"
            
            print(f"{column:<20} {status:<14} {missing_count:<15} {missing_pct:>6.2f}%")
        
        completeness_score = ((total_cells - total_missing) / total_cells) * 100
        
        print(f"\n{Colors.BOLD}OVERALL COMPLETENESS SCORE: {completeness_score:.2f}%{Colors.RESET}")
        
        if completeness_score >= 95:
            print(f"{Colors.GREEN}Status: EXCELLENT (>95% complete){Colors.RESET}")
        elif completeness_score >= 90:
            print(f"{Colors.YELLOW}Status: GOOD (90-95% complete){Colors.RESET}")
        elif completeness_score >= 80:
            print(f"{Colors.YELLOW}Status: ACCEPTABLE (80-90% complete){Colors.RESET}")
        else:
            print(f"{Colors.RED}Status: POOR (<80% complete){Colors.RESET}")
        
        self.assessment_results['Completeness'] = {
            'score': completeness_score,
            'missing_by_column': missing_data,
            'total_missing': total_missing
        }
        
        return missing_data
    
    # ========================================================================
    # DIMENSION 2: UNIQUENESS
    # ========================================================================
    
    def assess_uniqueness(self, key_columns=None):
        """
        Assess UNIQUENESS dimension
        - Duplicate records
        - Primary key violations
        - Near-duplicates
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}DIMENSION 2: UNIQUENESS{Colors.RESET}")
        print(f"{Colors.BLUE}{'-'*80}{Colors.RESET}")
        print("Definition: No duplicate records exist\n")
        
        # Exact duplicates
        exact_duplicates = self.df.duplicated().sum()
        total_records = len(self.df)
        duplicate_pct = (exact_duplicates / total_records) * 100 if total_records > 0 else 0
        
        print(f"{Colors.BOLD}Exact Duplicates:{Colors.RESET}")
        print(f"  Total Duplicates: {exact_duplicates}")
        print(f"  Percentage: {duplicate_pct:.2f}%")
        
        if exact_duplicates > 0:
            print(f"  {Colors.RED}✗ Found duplicate records{Colors.RESET}")
            print(f"\n  {Colors.YELLOW}Sample duplicate records:{Colors.RESET}")
            dup_records = self.df[self.df.duplicated(keep=False)].head(5)
            print(dup_records)
        else:
            print(f"  {Colors.GREEN}✓ No exact duplicates found{Colors.RESET}")
        
        # Duplicates by key columns
        if key_columns:
            print(f"\n{Colors.BOLD}Duplicates by Key Columns:{Colors.RESET}")
            for col in key_columns:
                if col in self.df.columns:
                    dup_count = self.df[col].duplicated().sum()
                    dup_pct = (dup_count / total_records) * 100
                    print(f"  {col}: {dup_count} duplicates ({dup_pct:.2f}%)")
                    
                    if dup_count > 0:
                        print(f"    {Colors.RED}✗ Non-unique values detected{Colors.RESET}")
        
        # Near-duplicate detection (fuzzy)
        print(f"\n{Colors.BOLD}Uniqueness Score:{Colors.RESET}")
        uniqueness_score = ((total_records - exact_duplicates) / total_records) * 100
        print(f"  {uniqueness_score:.2f}%")
        
        if uniqueness_score >= 99:
            print(f"  {Colors.GREEN}Status: EXCELLENT (>99% unique){Colors.RESET}")
        elif uniqueness_score >= 95:
            print(f"  {Colors.YELLOW}Status: GOOD (95-99% unique){Colors.RESET}")
        else:
            print(f"  {Colors.RED}Status: POOR (<95% unique){Colors.RESET}")
        
        self.assessment_results['Uniqueness'] = {
            'score': uniqueness_score,
            'exact_duplicates': exact_duplicates,
            'duplicate_percentage': duplicate_pct
        }
        
        return exact_duplicates
    
    # ========================================================================
    # DIMENSION 3: VALIDITY
    # ========================================================================
    
    def assess_validity(self, validation_rules=None):
        """
        Assess VALIDITY dimension
        - Data types
        - Format validation
        - Range constraints
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}DIMENSION 3: VALIDITY{Colors.RESET}")
        print(f"{Colors.BLUE}{'-'*80}{Colors.RESET}")
        print("Definition: Data conforms to required format, type, and structure\n")
        
        validity_issues = {}
        
        print(f"{Colors.BOLD}Data Types:{Colors.RESET}")
        print(f"{'Column':<20} {'Type':<20} {'Status':<10}")
        print("-" * 50)
        
        for column in self.df.columns:
            dtype = str(self.df[column].dtype)
            print(f"{column:<20} {dtype:<20} {Colors.GREEN}✓{Colors.RESET}")
        
        # Numeric validation
        print(f"\n{Colors.BOLD}Numeric Column Validation:{Colors.RESET}")
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            min_val = self.df[col].min()
            max_val = self.df[col].max()
            has_negative = (self.df[col] < 0).any()
            
            print(f"\n  {col}:")
            print(f"    Min: {min_val}, Max: {max_val}")
            
            if has_negative:
                print(f"    {Colors.YELLOW}⚠ Contains negative values{Colors.RESET}")
                validity_issues[col] = 'negative_values'
            else:
                print(f"    {Colors.GREEN}✓ All values valid{Colors.RESET}")
        
        # String validation
        print(f"\n{Colors.BOLD}String Column Validation:{Colors.RESET}")
        string_cols = self.df.select_dtypes(include=['object']).columns
        
        for col in string_cols:
            empty_strings = (self.df[col] == '').sum()
            whitespace_only = self.df[col].str.strip().eq('').sum()
            
            print(f"\n  {col}:")
            if empty_strings > 0:
                print(f"    {Colors.YELLOW}⚠ {empty_strings} empty strings{Colors.RESET}")
            if whitespace_only > 0:
                print(f"    {Colors.YELLOW}⚠ {whitespace_only} whitespace-only values{Colors.RESET}")
            
            if empty_strings == 0 and whitespace_only == 0:
                print(f"    {Colors.GREEN}✓ No formatting issues{Colors.RESET}")
        
        # Custom validation rules
        if validation_rules:
            print(f"\n{Colors.BOLD}Custom Validation Rules:{Colors.RESET}")
            for rule_name, rule_func in validation_rules.items():
                try:
                    violations = rule_func(self.df)
                    if violations > 0:
                        print(f"  {rule_name}: {Colors.RED}✗ {violations} violations{Colors.RESET}")
                        validity_issues[rule_name] = violations
                    else:
                        print(f"  {rule_name}: {Colors.GREEN}✓ Passed{Colors.RESET}")
                except Exception as e:
                    print(f"  {rule_name}: {Colors.YELLOW}⚠ Error: {e}{Colors.RESET}")
        
        validity_score = 100 if len(validity_issues) == 0 else max(0, 100 - (len(validity_issues) * 10))
        print(f"\n{Colors.BOLD}Validity Score: {validity_score:.2f}%{Colors.RESET}")
        
        self.assessment_results['Validity'] = {
            'score': validity_score,
            'issues': validity_issues
        }
        
        return validity_issues
    
    # ========================================================================
    # DIMENSION 4: CONSISTENCY
    # ========================================================================
    
    def assess_consistency(self, categorical_columns=None):
        """
        Assess CONSISTENCY dimension
        - Standardization of categorical values
        - Format consistency
        - Value distribution
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}DIMENSION 4: CONSISTENCY{Colors.RESET}")
        print(f"{Colors.BLUE}{'-'*80}{Colors.RESET}")
        print("Definition: Data is uniform and standardized\n")
        
        consistency_issues = {}
        
        # Get categorical columns
        if categorical_columns is None:
            categorical_columns = self.df.select_dtypes(include=['object']).columns
        
        print(f"{Colors.BOLD}Categorical Value Analysis:{Colors.RESET}\n")
        
        for col in categorical_columns:
            if col in self.df.columns:
                unique_values = self.df[col].nunique()
                value_counts = self.df[col].value_counts()
                
                print(f"{Colors.CYAN}{col}:{Colors.RESET}")
                print(f"  Unique values: {unique_values}")
                print(f"  Top values:")
                
                for value, count in value_counts.head(5).items():
                    pct = (count / len(self.df)) * 100
                    print(f"    - {value}: {count} ({pct:.1f}%)")
                
                # Check for case inconsistencies
                if self.df[col].dtype == 'object':
                    upper_count = self.df[col].str.isupper().sum()
                    lower_count = self.df[col].str.islower().sum()
                    mixed_case = unique_values - upper_count - lower_count
                    
                    if upper_count > 0 and lower_count > 0:
                        print(f"  {Colors.YELLOW}⚠ Mixed case values detected{Colors.RESET}")
                        consistency_issues[col] = 'mixed_case'
                    else:
                        print(f"  {Colors.GREEN}✓ Case consistent{Colors.RESET}")
                
                print()
        
        consistency_score = 100 if len(consistency_issues) == 0 else max(0, 100 - (len(consistency_issues) * 15))
        print(f"{Colors.BOLD}Consistency Score: {consistency_score:.2f}%{Colors.RESET}")
        
        self.assessment_results['Consistency'] = {
            'score': consistency_score,
            'issues': consistency_issues
        }
        
        return consistency_issues
    
    # ========================================================================
    # DIMENSION 5: ACCURACY
    # ========================================================================
    
    def assess_accuracy(self, accuracy_rules=None):
        """
        Assess ACCURACY dimension
        - Range validation
        - Business rule validation
        - Statistical outliers
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}DIMENSION 5: ACCURACY{Colors.RESET}")
        print(f"{Colors.BLUE}{'-'*80}{Colors.RESET}")
        print("Definition: Data correctly represents real-world values\n")
        
        accuracy_issues = {}
        
        # Numeric range analysis
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        print(f"{Colors.BOLD}Numeric Column Statistics:{Colors.RESET}\n")
        
        for col in numeric_cols:
            print(f"{Colors.CYAN}{col}:{Colors.RESET}")
            
            # Calculate statistics
            mean = self.df[col].mean()
            std = self.df[col].std()
            median = self.df[col].median()
            q1 = self.df[col].quantile(0.25)
            q3 = self.df[col].quantile(0.75)
            iqr = q3 - q1
            
            print(f"  Mean: {mean:.2f}")
            print(f"  Median: {median:.2f}")
            print(f"  Std Dev: {std:.2f}")
            print(f"  Range: [{self.df[col].min()}, {self.df[col].max()}]")
            
            # Outlier detection (IQR method)
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
            outlier_pct = (len(outliers) / len(self.df)) * 100 if len(self.df) > 0 else 0
            
            if len(outliers) > 0:
                print(f"  {Colors.YELLOW}⚠ Outliers detected: {len(outliers)} ({outlier_pct:.2f}%){Colors.RESET}")
                accuracy_issues[col] = {
                    'outlier_count': len(outliers),
                    'outlier_percentage': outlier_pct
                }
            else:
                print(f"  {Colors.GREEN}✓ No outliers detected{Colors.RESET}")
            
            print()
        
        # Custom accuracy rules
        if accuracy_rules:
            print(f"{Colors.BOLD}Custom Accuracy Rules:{Colors.RESET}\n")
            
            for rule_name, rule_func in accuracy_rules.items():
                try:
                    violations = rule_func(self.df)
                    if violations > 0:
                        print(f"  {rule_name}: {Colors.RED}✗ {violations} violations{Colors.RESET}")
                        accuracy_issues[rule_name] = violations
                    else:
                        print(f"  {rule_name}: {Colors.GREEN}✓ Passed{Colors.RESET}")
                except Exception as e:
                    print(f"  {rule_name}: {Colors.YELLOW}⚠ Error: {e}{Colors.RESET}")
            
            print()
        
        accuracy_score = 100 if len(accuracy_issues) == 0 else max(0, 100 - (len(accuracy_issues) * 10))
        print(f"{Colors.BOLD}Accuracy Score: {accuracy_score:.2f}%{Colors.RESET}")
        
        self.assessment_results['Accuracy'] = {
            'score': accuracy_score,
            'issues': accuracy_issues
        }
        
        return accuracy_issues
    
    # ========================================================================
    # DIMENSION 6: TIMELINESS
    # ========================================================================
    
    def assess_timeliness(self, date_column=None, max_age_days=None):
        """
        Assess TIMELINESS dimension
        - Data freshness
        - Last update time
        - Data age
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}DIMENSION 6: TIMELINESS{Colors.RESET}")
        print(f"{Colors.BLUE}{'-'*80}{Colors.RESET}")
        print("Definition: Data is current and meets delivery requirements\n")
        
        timeliness_issues = {}
        
        # Check for datetime columns
        datetime_cols = self.df.select_dtypes(include=['datetime64']).columns
        
        if len(datetime_cols) > 0:
            print(f"{Colors.BOLD}Date/Time Columns Found:{Colors.RESET}\n")
            
            for col in datetime_cols:
                print(f"{Colors.CYAN}{col}:{Colors.RESET}")
                
                min_date = self.df[col].min()
                max_date = self.df[col].max()
                today = pd.Timestamp.now()
                data_age = today - max_date
                
                print(f"  Earliest: {min_date}")
                print(f"  Latest: {max_date}")
                print(f"  Data Age: {data_age.days} days")
                
                # Check if data is stale
                if max_age_days and data_age.days > max_age_days:
                    print(f"  {Colors.RED}✗ Data is stale (older than {max_age_days} days){Colors.RESET}")
                    timeliness_issues[col] = f'stale_{data_age.days}_days'
                elif data_age.days > 30:
                    print(f"  {Colors.YELLOW}⚠ Data is older than 30 days{Colors.RESET}")
                else:
                    print(f"  {Colors.GREEN}✓ Data is current{Colors.RESET}")
                
                print()
        else:
            print(f"{Colors.YELLOW}⚠ No datetime columns found for timeliness assessment{Colors.RESET}\n")
        
        timeliness_score = 100 if len(timeliness_issues) == 0 else 50
        print(f"{Colors.BOLD}Timeliness Score: {timeliness_score:.2f}%{Colors.RESET}")
        
        self.assessment_results['Timeliness'] = {
            'score': timeliness_score,
            'issues': timeliness_issues
        }
        
        return timeliness_issues
    
    # ========================================================================
    # OVERALL QUALITY SCORE
    # ========================================================================
    
    def calculate_overall_score(self):
        """
        Calculate overall data quality score across all dimensions
        """
        print(f"\n{Colors.HEADER}{'='*80}{Colors.RESET}")
        print(f"{Colors.HEADER}{Colors.BOLD}OVERALL DATA QUALITY ASSESSMENT{Colors.RESET}")
        print(f"{Colors.HEADER}{'='*80}{Colors.RESET}\n")
        
        # Extract scores
        scores = {}
        for dimension, results in self.assessment_results.items():
            if 'score' in results:
                scores[dimension] = results['score']
        
        # Display individual scores
        print(f"{Colors.BOLD}Dimension Scores:{Colors.RESET}\n")
        print(f"{'Dimension':<20} {'Score':<15} {'Status':<20}")
        print("-" * 55)
        
        for dimension, score in scores.items():
            if score >= 95:
                status = f"{Colors.GREEN}EXCELLENT{Colors.RESET}"
            elif score >= 80:
                status = f"{Colors.YELLOW}GOOD{Colors.RESET}"
            elif score >= 60:
                status = f"{Colors.YELLOW}ACCEPTABLE{Colors.RESET}"
            else:
                status = f"{Colors.RED}POOR{Colors.RESET}"
            
            print(f"{dimension:<20} {score:>6.2f}%{'':<8} {status:<20}")
        
        # Calculate weighted average (all dimensions weighted equally for now)
        overall_score = np.mean(list(scores.values())) if scores else 0
        
        # Determine overall status
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Overall Data Quality Score: {overall_score:.2f}%{Colors.RESET}\n")
        
        if overall_score >= 95:
            status = f"{Colors.GREEN}{Colors.BOLD}EXCELLENT - Ready for production{Colors.RESET}"
        elif overall_score >= 85:
            status = f"{Colors.YELLOW}{Colors.BOLD}GOOD - Minor issues to address{Colors.RESET}"
        elif overall_score >= 70:
            status = f"{Colors.YELLOW}{Colors.BOLD}ACCEPTABLE - Significant issues to address{Colors.RESET}"
        else:
            status = f"{Colors.RED}{Colors.BOLD}POOR - Major cleaning required{Colors.RESET}"
        
        print(f"Status: {status}\n")
        
        self.assessment_results['Overall_Score'] = overall_score
        
        return overall_score
    
    # ========================================================================
    # GENERATE REPORT
    # ========================================================================
    
    def generate_report(self, output_file=None):
        """
        Generate a detailed quality report
        """
        print(f"\n{Colors.BOLD}Generating Quality Report...{Colors.RESET}")
        
        report = {
            'dataset_name': self.name,
            'timestamp': self.timestamp.isoformat(),
            'dimensions': self.assessment_results
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"{Colors.GREEN}✓ Report saved to: {output_file}{Colors.RESET}")
        
        return report
    
    # ========================================================================
    # RUN FULL ASSESSMENT
    # ========================================================================
    
    def run_full_assessment(self, categorical_cols=None, key_cols=None,
                           validation_rules=None, accuracy_rules=None,
                           date_column=None, max_age_days=None):
        """
        Run complete assessment across all dimensions
        
        Parameters:
        -----------
        categorical_cols : list
            Columns to check for consistency
        key_cols : list
            Key columns to check for uniqueness
        validation_rules : dict
            Custom validation rules
        accuracy_rules : dict
            Custom accuracy rules
        date_column : str
            Date column for timeliness check
        max_age_days : int
            Maximum acceptable data age in days
        """
        
        # Run all assessments
        self.assess_completeness()
        self.assess_uniqueness(key_cols)
        self.assess_validity(validation_rules)
        self.assess_consistency(categorical_cols)
        self.assess_accuracy(accuracy_rules)
        self.assess_timeliness(date_column, max_age_days)
        
        # Calculate overall score
        overall_score = self.calculate_overall_score()
        
        return overall_score


# ============================================================================
# EXAMPLE USAGE & DEMONSTRATION
# ============================================================================

def main():
    """
    Example usage of the DataQualityAssessment class
    """
    
    print("\n" + "="*80)
    print("DATA QUALITY ASSESSMENT - EXAMPLE DEMONSTRATION")
    print("="*80)
    
    # ========================================================================
    # Load sample data from GitHub
    # ========================================================================
    
    print("\n[STEP 1] Loading Sample Data...")
    print("-" * 80)
    
    url = "https://raw.githubusercontent.com/YOUR-USERNAME/data-cleaning-exercises/main/data/customer_orders_messy.csv"
    
    try:
        response = requests.get(url, timeout=10)
        df = pd.read_csv(io.StringIO(response.text))
        print(f"{Colors.GREEN}✓ Data loaded from GitHub{Colors.RESET}")
    except:
        print(f"{Colors.YELLOW}⚠ Using local fallback data{Colors.RESET}")
        # Create sample data
        df = pd.DataFrame({
            'OrderID': [1001, 1002, 1003, 1003, 1004, 1005],
            'CustomerName': ['John Doe', 'jane smith', 'John Doe', 'John Doe', 'Bob Johnson', None],
            'Email': ['john@email.com', 'jane@email.com', 'john@email.com', 'john@email.com', 'bob@email.com', 'alice@email.com'],
            'Amount': [100.50, 250.00, 100.50, -50, 999999, 75.25],
            'OrderDate': ['2023-01-15', '2023-01-16', '2023-01-15', '2023-01-17', '2023-01-18', '2023-01-19'],
            'Status': ['Completed', 'Completed', 'Completed', 'Pending', 'Shipped', 'active']
        })
    
    # ========================================================================
    # Define custom rules
    # ========================================================================
    
    print("\n[STEP 2] Defining Custom Rules...")
    print("-" * 80)
    
    # Validation rules
    validation_rules = {
        'Amount_must_be_positive': lambda df: (df['Amount'] < 0).sum(),
        'Amount_must_be_reasonable': lambda df: (df['Amount'] > 100000).sum()
    }
    
    # Accuracy rules
    accuracy_rules = {
        'Order_ID_must_be_unique': lambda df: df['OrderID'].duplicated().sum(),
        'Email_must_be_valid': lambda df: ~df['Email'].str.contains('@', na=False).sum()
    }
    
    print(f"{Colors.GREEN}✓ Custom rules defined{Colors.RESET}")
    
    # ========================================================================
    # Run Assessment
    # ========================================================================
    
    print("\n[STEP 3] Running Data Quality Assessment...")
    print("-" * 80)
    
    # Create assessment object
    assessment = DataQualityAssessment(df, name="Customer Orders Dataset")
    
    # Run full assessment
    overall_score = assessment.run_full_assessment(
        categorical_cols=['Status', 'CustomerName'],
        key_cols=['OrderID'],
        validation_rules=validation_rules,
        accuracy_rules=accuracy_rules,
        date_column='OrderDate',
        max_age_days=90
    )
    
    # ========================================================================
    # Generate Report
    # ========================================================================
    
    print("\n[STEP 4] Generating Report...")
    print("-" * 80)
    
    report = assessment.generate_report('data_quality_report.json')
    
    print(f"\n{Colors.GREEN}✓ Assessment complete!{Colors.RESET}")
    print(f"{Colors.HEADER}{'='*80}{Colors.RESET}\n")


if __name__ == "__main__":
    main()