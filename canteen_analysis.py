import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class CanteenAnalyzer:
    def __init__(self):
        self.menu_data = None
        self.transaction_data = None
        
    def load_menu_data(self, menu_json):
        """Load menu data from JSON format"""
        try:
            with open(menu_json, 'r', encoding='utf-8') as f:
                self.menu_data = json.load(f)
            print(f"Loaded menu data for {len(self.menu_data)} days")
        except FileNotFoundError:
            print("Menu file not found. Creating sample data...")
            self.create_sample_menu_data()
    
    def load_transaction_data(self, transaction_xlsx):
        """Load transaction data from Excel format"""
        try:
            self.transaction_data = pd.read_excel(transaction_xlsx)
            print(f"Loaded transaction data: {self.transaction_data.shape}")
        except FileNotFoundError:
            print("Transaction file not found. Creating sample data...")
            self.create_sample_transaction_data()
    
    def create_sample_menu_data(self):
        """Create sample menu data for demonstration"""
        sample_menu = {
            "date": "2024-01-15",
            "menus": [
                {
                    "corner": "01",
                    "corner_index": 1,
                    "main": "Cơm gà xối mỡ",
                    "dishes": ["Canh chua cá lóc", "Rau muống xào tỏi"],
                    "kcal": 650
                },
                {
                    "corner": "02", 
                    "corner_index": 2,
                    "main": "Phở bò",
                    "dishes": ["Giá trụng", "Rau thơm"],
                    "kcal": 550
                },
                {
                    "corner": "03",
                    "corner_index": 3, 
                    "main": "Bún chả",
                    "dishes": ["Rau sống", "Nước mắm"],
                    "kcal": 600
                },
                {
                    "corner": "04",
                    "corner_index": 4,
                    "main": "Cơm tấm sườn",
                    "dishes": ["Canh bí đỏ", "Dưa leo"],
                    "kcal": 700
                }
            ]
        }
        self.menu_data = [sample_menu]
    
    def create_sample_transaction_data(self):
        """Create sample transaction data for demonstration"""
        np.random.seed(42)
        
        # Generate sample data
        dates = pd.date_range('2024-01-01', '2024-01-31', freq='D')
        employees = [f"EMP{i:04d}" for i in range(1, 201)]
        depts = ["IT", "HR", "Finance", "Marketing", "Operations", "Sales"]
        corners = ["01", "02", "03", "04"]
        
        data = []
        for date in dates:
            if date.weekday() < 5:  # Weekdays only
                # Generate 150-200 transactions per day
                n_transactions = np.random.randint(150, 201)
                
                for _ in range(n_transactions):
                    # Different lunch times for different departments
                    dept = np.random.choice(depts)
                    if dept in ["IT", "HR"]:
                        meal_time = date + timedelta(hours=11, minutes=np.random.randint(0, 30))
                    elif dept in ["Finance", "Marketing"]:
                        meal_time = date + timedelta(hours=11, minutes=np.random.randint(30, 60))
                    else:
                        meal_time = date + timedelta(hours=12, minutes=np.random.randint(0, 30))
                    
                    data.append({
                        'Meal Date': meal_time,
                        'Food Distribution Counter': np.random.choice(corners),
                        'Company': 'Company A',
                        'Employee No': np.random.choice(employees),
                        'Name': f"Employee {np.random.randint(1, 1000)}",
                        'Dept.': dept
                    })
        
        self.transaction_data = pd.DataFrame(data)
        print(f"Created sample transaction data: {self.transaction_data.shape}")
    
    def analyze_transaction_patterns(self):
        """Analyze transaction patterns"""
        if self.transaction_data is None:
            print("No transaction data loaded")
            return
        
        # Convert to datetime
        self.transaction_data['Meal Date'] = pd.to_datetime(self.transaction_data['Meal Date'])
        self.transaction_data['Date'] = self.transaction_data['Meal Date'].dt.date
        self.transaction_data['Hour'] = self.transaction_data['Meal Date'].dt.hour
        self.transaction_data['Minute'] = self.transaction_data['Meal Date'].dt.minute
        
        # Analysis
        print("\n=== TRANSACTION PATTERN ANALYSIS ===")
        
        # Daily transaction count
        daily_counts = self.transaction_data.groupby('Date').size()
        print(f"Average daily transactions: {daily_counts.mean():.1f}")
        print(f"Min daily transactions: {daily_counts.min()}")
        print(f"Max daily transactions: {daily_counts.max()}")
        
        # Counter distribution
        counter_dist = self.transaction_data['Food Distribution Counter'].value_counts()
        print(f"\nCounter distribution:\n{counter_dist}")
        
        # Department distribution
        dept_dist = self.transaction_data['Dept.'].value_counts()
        print(f"\nDepartment distribution:\n{dept_dist}")
        
        # Time distribution
        time_dist = self.transaction_data.groupby('Hour').size()
        print(f"\nPeak lunch hours:\n{time_dist}")
        
        return {
            'daily_counts': daily_counts,
            'counter_dist': counter_dist,
            'dept_dist': dept_dist,
            'time_dist': time_dist
        }
    
    def visualize_data(self):
        """Create comprehensive visualizations"""
        if self.transaction_data is None:
            print("No transaction data loaded")
            return
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Canteen Transaction Analysis', fontsize=16, fontweight='bold')
        
        # 1. Daily transaction trend
        daily_counts = self.transaction_data.groupby('Date').size()
        axes[0, 0].plot(daily_counts.index, daily_counts.values, marker='o')
        axes[0, 0].set_title('Daily Transaction Trend')
        axes[0, 0].set_xlabel('Date')
        axes[0, 0].set_ylabel('Number of Transactions')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Counter distribution
        counter_dist = self.transaction_data['Food Distribution Counter'].value_counts()
        axes[0, 1].pie(counter_dist.values, labels=counter_dist.index, autopct='%1.1f%%')
        axes[0, 1].set_title('Distribution by Counter')
        
        # 3. Department distribution
        dept_dist = self.transaction_data['Dept.'].value_counts()
        axes[0, 2].bar(dept_dist.index, dept_dist.values)
        axes[0, 2].set_title('Distribution by Department')
        axes[0, 2].set_xlabel('Department')
        axes[0, 2].set_ylabel('Number of Transactions')
        axes[0, 2].tick_params(axis='x', rotation=45)
        
        # 4. Hourly distribution
        time_dist = self.transaction_data.groupby('Hour').size()
        axes[1, 0].bar(time_dist.index, time_dist.values)
        axes[1, 0].set_title('Hourly Distribution')
        axes[1, 0].set_xlabel('Hour')
        axes[1, 0].set_ylabel('Number of Transactions')
        
        # 5. Counter vs Department heatmap
        counter_dept = pd.crosstab(self.transaction_data['Food Distribution Counter'], 
                                  self.transaction_data['Dept.'])
        sns.heatmap(counter_dept, annot=True, fmt='d', cmap='YlOrRd', ax=axes[1, 1])
        axes[1, 1].set_title('Counter vs Department Heatmap')
        
        # 6. Time series by counter
        time_counter = self.transaction_data.groupby(['Hour', 'Food Distribution Counter']).size().unstack(fill_value=0)
        time_counter.plot(kind='line', marker='o', ax=axes[1, 2])
        axes[1, 2].set_title('Hourly Trend by Counter')
        axes[1, 2].set_xlabel('Hour')
        axes[1, 2].set_ylabel('Number of Transactions')
        axes[1, 2].legend(title='Counter')
        
        plt.tight_layout()
        plt.show()
    
    def create_interactive_dashboard(self):
        """Create interactive Plotly dashboard"""
        if self.transaction_data is None:
            print("No transaction data loaded")
            return
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Daily Transaction Trend', 'Counter Distribution', 
                          'Department Distribution', 'Hourly Distribution'),
            specs=[[{"type": "scatter"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # 1. Daily trend
        daily_counts = self.transaction_data.groupby('Date').size()
        fig.add_trace(
            go.Scatter(x=daily_counts.index, y=daily_counts.values, 
                      mode='lines+markers', name='Daily Transactions'),
            row=1, col=1
        )
        
        # 2. Counter distribution
        counter_dist = self.transaction_data['Food Distribution Counter'].value_counts()
        fig.add_trace(
            go.Pie(labels=counter_dist.index, values=counter_dist.values, name='Counter'),
            row=1, col=2
        )
        
        # 3. Department distribution
        dept_dist = self.transaction_data['Dept.'].value_counts()
        fig.add_trace(
            go.Bar(x=dept_dist.index, y=dept_dist.values, name='Department'),
            row=2, col=1
        )
        
        # 4. Hourly distribution
        time_dist = self.transaction_data.groupby('Hour').size()
        fig.add_trace(
            go.Bar(x=time_dist.index, y=time_dist.values, name='Hour'),
            row=2, col=2
        )
        
        fig.update_layout(height=800, title_text="Canteen Transaction Dashboard")
        fig.show()
    
    def suggest_solution(self):
        """Suggest solution approach"""
        print("\n=== SOLUTION SUGGESTION ===")
        print("1. DATA PREPROCESSING:")
        print("   - Clean and validate transaction data")
        print("   - Extract features: day of week, month, season")
        print("   - Create menu features: dish type, kcal, popularity")
        print("   - Merge transaction data with menu data")
        
        print("\n2. FEATURE ENGINEERING:")
        print("   - Historical demand patterns by counter")
        print("   - Department preferences")
        print("   - Time-based patterns (hour, day of week)")
        print("   - Menu similarity features")
        print("   - Weather data (if available)")
        
        print("\n3. MODELING APPROACH:")
        print("   - Time series forecasting (ARIMA, Prophet)")
        print("   - Machine learning (Random Forest, XGBoost)")
        print("   - Deep learning (LSTM, GRU)")
        print("   - Ensemble methods")
        
        print("\n4. EVALUATION METRICS:")
        print("   - Mean Absolute Error (MAE)")
        print("   - Root Mean Square Error (RMSE)")
        print("   - Mean Absolute Percentage Error (MAPE)")
        
        print("\n5. IMPLEMENTATION STEPS:")
        print("   - Data collection and cleaning")
        print("   - Feature engineering")
        print("   - Model training and validation")
        print("   - Real-time prediction system")
        print("   - Monitoring and retraining")

def main():
    """Main function to run the analysis"""
    analyzer = CanteenAnalyzer()
    
    # Load data (will create sample data if files not found)
    analyzer.load_menu_data("menu_data.json")
    analyzer.load_transaction_data("transaction_data.xlsx")
    
    # Analyze patterns
    patterns = analyzer.analyze_transaction_patterns()
    
    # Create visualizations
    analyzer.visualize_data()
    analyzer.create_interactive_dashboard()
    
    # Suggest solution
    analyzer.suggest_solution()

if __name__ == "__main__":
    main() 