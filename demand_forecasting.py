import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
import xgboost as xgb
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

class CanteenDemandForecaster:
    def __init__(self):
        self.models = {}
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        
    def preprocess_data(self, transaction_data, menu_data):
        """Preprocess and merge transaction and menu data"""
        print("Preprocessing data...")
        
        # Convert transaction data
        transaction_data['Meal Date'] = pd.to_datetime(transaction_data['Meal Date'])
        transaction_data['Date'] = transaction_data['Meal Date'].dt.date
        transaction_data['Hour'] = transaction_data['Meal Date'].dt.hour
        transaction_data['DayOfWeek'] = transaction_data['Meal Date'].dt.dayofweek
        transaction_data['Month'] = transaction_data['Meal Date'].dt.month
        transaction_data['WeekOfYear'] = transaction_data['Meal Date'].dt.isocalendar().week
        
        # Create menu features
        menu_features = self._extract_menu_features(menu_data)
        
        # Merge data
        merged_data = self._merge_data(transaction_data, menu_features)
        
        return merged_data
    
    def _extract_menu_features(self, menu_data):
        """Extract features from menu data"""
        menu_features = []
        
        for day_menu in menu_data:
            date = day_menu['date']
            menus = day_menu['menus']
            
            for menu in menus:
                menu_features.append({
                    'Date': date,
                    'Corner': menu['corner'],
                    'CornerIndex': menu['corner_index'],
                    'MainDish': menu['main'],
                    'SideDishes': len(menu['dishes']),
                    'Kcal': menu['kcal'],
                    'DishType': self._categorize_dish(menu['main']),
                    'IsPopular': self._is_popular_dish(menu['main'])
                })
        
        return pd.DataFrame(menu_features)
    
    def _categorize_dish(self, dish_name):
        """Categorize dish type"""
        dish_name = dish_name.lower()
        
        if any(word in dish_name for word in ['cơm', 'rice']):
            return 'rice'
        elif any(word in dish_name for word in ['phở', 'pho']):
            return 'noodle_soup'
        elif any(word in dish_name for word in ['bún', 'bun']):
            return 'noodle'
        elif any(word in dish_name for word in ['chả', 'cha']):
            return 'grilled'
        else:
            return 'other'
    
    def _is_popular_dish(self, dish_name):
        """Determine if dish is popular based on keywords"""
        popular_keywords = ['gà', 'ga', 'phở', 'pho', 'bún', 'bun', 'sườn', 'suon']
        dish_name = dish_name.lower()
        
        return any(keyword in dish_name for keyword in popular_keywords)
    
    def _merge_data(self, transaction_data, menu_features):
        """Merge transaction and menu data"""
        # Aggregate transactions by date, hour, corner
        daily_demand = transaction_data.groupby(['Date', 'Hour', 'Food Distribution Counter']).size().reset_index()
        daily_demand.columns = ['Date', 'Hour', 'Corner', 'Demand']
        
        # Merge with menu features
        merged = pd.merge(daily_demand, menu_features, 
                         on=['Date', 'Corner'], how='left')
        
        # Add department features
        dept_demand = transaction_data.groupby(['Date', 'Hour', 'Food Distribution Counter', 'Dept.']).size().reset_index()
        dept_demand.columns = ['Date', 'Hour', 'Corner', 'Dept', 'DeptDemand']
        
        merged = pd.merge(merged, dept_demand, 
                         on=['Date', 'Hour', 'Corner'], how='left')
        
        return merged
    
    def engineer_features(self, data):
        """Engineer features for prediction"""
        print("Engineering features...")
        
        # Time-based features
        data['Date'] = pd.to_datetime(data['Date'])
        data['DayOfWeek'] = data['Date'].dt.dayofweek
        data['Month'] = data['Date'].dt.month
        data['WeekOfYear'] = data['Date'].dt.isocalendar().week
        data['IsWeekend'] = data['DayOfWeek'].isin([5, 6]).astype(int)
        
        # Historical demand features
        data = self._add_historical_features(data)
        
        # Department features
        data = self._add_department_features(data)
        
        # Menu features
        data = self._add_menu_features(data)
        
        return data
    
    def _add_historical_features(self, data):
        """Add historical demand features"""
        # Average demand by corner, hour, day of week
        historical_stats = data.groupby(['Corner', 'Hour', 'DayOfWeek'])['Demand'].agg(['mean', 'std']).reset_index()
        historical_stats.columns = ['Corner', 'Hour', 'DayOfWeek', 'HistMean', 'HistStd']
        
        data = pd.merge(data, historical_stats, on=['Corner', 'Hour', 'DayOfWeek'], how='left')
        
        # Fill missing values
        data['HistMean'] = data['HistMean'].fillna(data['Demand'].mean())
        data['HistStd'] = data['HistStd'].fillna(data['Demand'].std())
        
        return data
    
    def _add_department_features(self, data):
        """Add department-related features"""
        # Department preferences by corner
        dept_preferences = data.groupby(['Corner', 'Dept'])['DeptDemand'].mean().reset_index()
        dept_preferences.columns = ['Corner', 'Dept', 'DeptPreference']
        
        data = pd.merge(data, dept_preferences, on=['Corner', 'Dept'], how='left')
        
        return data
    
    def _add_menu_features(self, data):
        """Add menu-related features"""
        # Encode categorical features
        categorical_features = ['Corner', 'Dept', 'DishType', 'MainDish']
        
        for feature in categorical_features:
            if feature in data.columns:
                le = LabelEncoder()
                data[f'{feature}_Encoded'] = le.fit_transform(data[feature].astype(str))
                self.label_encoders[feature] = le
        
        return data
    
    def prepare_features(self, data):
        """Prepare final feature set for modeling"""
        print("Preparing features for modeling...")
        
        # Select features for modeling
        feature_columns = [
            'Hour', 'DayOfWeek', 'Month', 'WeekOfYear', 'IsWeekend',
            'CornerIndex', 'SideDishes', 'Kcal', 'IsPopular',
            'HistMean', 'HistStd', 'DeptPreference',
            'Corner_Encoded', 'Dept_Encoded', 'DishType_Encoded'
        ]
        
        # Filter available columns
        available_features = [col for col in feature_columns if col in data.columns]
        self.feature_columns = available_features
        
        X = data[available_features].fillna(0)
        y = data['Demand']
        
        return X, y
    
    def train_models(self, X, y):
        """Train multiple models"""
        print("Training models...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train_scaled, y_train)
        
        # Train XGBoost
        xgb_model = xgb.XGBRegressor(n_estimators=100, random_state=42)
        xgb_model.fit(X_train_scaled, y_train)
        
        # Evaluate models
        models = {
            'RandomForest': rf_model,
            'XGBoost': xgb_model
        }
        
        for name, model in models.items():
            y_pred = model.predict(X_test_scaled)
            
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            print(f"\n{name} Performance:")
            print(f"MAE: {mae:.2f}")
            print(f"RMSE: {rmse:.2f}")
            print(f"R²: {r2:.3f}")
        
        self.models = models
        return models
    
    def predict_demand(self, menu_data, date, hour):
        """Predict demand for a specific date and hour"""
        if not self.models:
            print("Models not trained yet!")
            return None
        
        # Create prediction data
        prediction_data = self._create_prediction_data(menu_data, date, hour)
        
        # Prepare features
        X_pred = prediction_data[self.feature_columns].fillna(0)
        X_pred_scaled = self.scaler.transform(X_pred)
        
        # Make predictions
        predictions = {}
        for name, model in self.models.items():
            pred = model.predict(X_pred_scaled)
            predictions[name] = pred
        
        # Combine predictions (ensemble)
        ensemble_pred = np.mean([pred for pred in predictions.values()], axis=0)
        
        # Create result
        result = []
        for i, corner in enumerate(prediction_data['Corner']):
            result.append({
                'Corner': corner,
                'PredictedDemand': int(round(ensemble_pred[i])),
                'RandomForest': int(round(predictions['RandomForest'][i])),
                'XGBoost': int(round(predictions['XGBoost'][i]))
            })
        
        return result
    
    def _create_prediction_data(self, menu_data, date, hour):
        """Create data for prediction"""
        # Find menu for the date
        day_menu = None
        for menu in menu_data:
            if menu['date'] == date:
                day_menu = menu
                break
        
        if not day_menu:
            print(f"No menu found for date {date}")
            return None
        
        # Create prediction records for each corner
        prediction_records = []
        
        for menu in day_menu['menus']:
            # Create base record
            record = {
                'Date': date,
                'Hour': hour,
                'Corner': menu['corner'],
                'CornerIndex': menu['corner_index'],
                'MainDish': menu['main'],
                'SideDishes': len(menu['dishes']),
                'Kcal': menu['kcal'],
                'DishType': self._categorize_dish(menu['main']),
                'IsPopular': self._is_popular_dish(menu['main'])
            }
            
            # Add time features
            date_obj = pd.to_datetime(date)
            record['DayOfWeek'] = date_obj.dayofweek
            record['Month'] = date_obj.month
            record['WeekOfYear'] = date_obj.isocalendar().week
            record['IsWeekend'] = int(record['DayOfWeek'] in [5, 6])
            
            # Add encoded features
            for feature in ['Corner', 'MainDish', 'DishType']:
                if feature in self.label_encoders:
                    record[f'{feature}_Encoded'] = self.label_encoders[feature].transform([record[feature]])[0]
            
            prediction_records.append(record)
        
        return pd.DataFrame(prediction_records)

def main():
    """Main function to demonstrate the forecasting system"""
    forecaster = CanteenDemandForecaster()
    
    # Load sample data (you would load your actual data here)
    print("Loading sample data...")
    
    # Create sample transaction data
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', '2024-01-31', freq='D')
    employees = [f"EMP{i:04d}" for i in range(1, 201)]
    depts = ["IT", "HR", "Finance", "Marketing", "Operations", "Sales"]
    corners = ["01", "02", "03", "04"]
    
    transaction_data = []
    for date in dates:
        if date.weekday() < 5:  # Weekdays only
            n_transactions = np.random.randint(150, 201)
            
            for _ in range(n_transactions):
                dept = np.random.choice(depts)
                if dept in ["IT", "HR"]:
                    meal_time = date + timedelta(hours=11, minutes=np.random.randint(0, 30))
                elif dept in ["Finance", "Marketing"]:
                    meal_time = date + timedelta(hours=11, minutes=np.random.randint(30, 60))
                else:
                    meal_time = date + timedelta(hours=12, minutes=np.random.randint(0, 30))
                
                transaction_data.append({
                    'Meal Date': meal_time,
                    'Food Distribution Counter': np.random.choice(corners),
                    'Company': 'Company A',
                    'Employee No': np.random.choice(employees),
                    'Name': f"Employee {np.random.randint(1, 1000)}",
                    'Dept.': dept
                })
    
    transaction_df = pd.DataFrame(transaction_data)
    
    # Create sample menu data
    menu_data = []
    for date in dates:
        if date.weekday() < 5:
            menu_data.append({
                "date": date.strftime('%Y-%m-%d'),
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
            })
    
    # Preprocess data
    processed_data = forecaster.preprocess_data(transaction_df, menu_data)
    
    # Engineer features
    feature_data = forecaster.engineer_features(processed_data)
    
    # Prepare features for modeling
    X, y = forecaster.prepare_features(feature_data)
    
    # Train models
    models = forecaster.train_models(X, y)
    
    # Make prediction
    print("\n=== DEMAND PREDICTION ===")
    prediction_date = "2024-02-01"
    prediction_hour = 12
    
    predictions = forecaster.predict_demand(menu_data, prediction_date, prediction_hour)
    
    if predictions:
        print(f"\nPredicted demand for {prediction_date} at {prediction_hour}:00:")
        for pred in predictions:
            print(f"Corner {pred['Corner']}: {pred['PredictedDemand']} meals")
            print(f"  - Random Forest: {pred['RandomForest']}")
            print(f"  - XGBoost: {pred['XGBoost']}")

if __name__ == "__main__":
    main() 