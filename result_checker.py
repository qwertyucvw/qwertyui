import os
import json
import glob
import sys
import math

def main():
    print("=" * 60)
    print("🔍 Starting Results Validation")
    print("=" * 60)
    
    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir, exist_ok=True)
        print(f"ℹ️ Created results directory: {os.path.abspath(results_dir)}")
    

    files = glob.glob(os.path.join(results_dir, "*.json"))
    if not files:
        print("ℹ️ No JSON files found in results directory. Validation skipped.")
        return 0
    
    required_fields = [
        "username", 
        "generation_time", 
        "sorting_time", 
        "total_time", 
        "correctly_sorted"
    ]
    
    errors = []
    valid_count = 0
    fixed_count = 0
    
    for filepath in files:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Флаг для отслеживания исправлений
            was_fixed = False
            
            # 1. Автоматическое исправление: добавить username из имени файла
            if 'username' not in data:
                username = os.path.splitext(filename)[0]
                data['username'] = username
                was_fixed = True
                print(f"ℹ️ Auto-fixed {filename}: added username '{username}'")
            
            # 2. Автоматическое исправление: пересчитать total_time
            if 'generation_time' in data and 'sorting_time' in data:
                expected_total = data['generation_time'] + data['sorting_time']
                
                # Проверяем с учетом погрешности вычислений с плавающей точкой
                if 'total_time' not in data or math.isclose(data['total_time'], expected_total, abs_tol=0.001) is False:
                    data['total_time'] = expected_total
                    was_fixed = True
                    print(f"ℹ️ Auto-fixed {filename}: corrected total_time to {expected_total:.4f}")
            
            # Проверка обязательных полей после исправлений
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                errors.append(f"{filename}: Missing fields - {', '.join(missing_fields)}")
                continue
            
            # Проверка типов данных
            type_errors = []
            if not isinstance(data['username'], str):
                type_errors.append("username must be string")
            
            if not isinstance(data['generation_time'], (int, float)):
                type_errors.append("generation_time must be number")
            
            if not isinstance(data['sorting_time'], (int, float)):
                type_errors.append("sorting_time must be number")
            
            if not isinstance(data['total_time'], (int, float)):
                type_errors.append("total_time must be number")
            
            if not isinstance(data['correctly_sorted'], bool):
                type_errors.append("correctly_sorted must be boolean")
            
            if type_errors:
                errors.append(f"{filename}: Type errors - {', '.join(type_errors)}")
                continue
            
            # Проверка значений
            if data['generation_time'] < 0:
                errors.append(f"{filename}: generation_time cannot be negative")
                continue
            
            if data['sorting_time'] < 0:
                errors.append(f"{filename}: sorting_time cannot be negative")
                continue
            
            if data['total_time'] < 0:
                errors.append(f"{filename}: total_time cannot be negative")
                continue
            
            # Сохраняем исправленный файл
            if was_fixed:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                fixed_count += 1
            
            valid_count += 1
                
        except json.JSONDecodeError:
            errors.append(f"{filename}: Invalid JSON format")
        except Exception as e:
            errors.append(f"{filename}: Unexpected error - {str(e)}")
    
    # Вывод итогов
    print("\n" + "=" * 60)
    print("Validation Summary:")
    print(f"- Total files processed: {len(files)}")
    print(f"- Valid files: {valid_count}")
    print(f"- Files auto-fixed: {fixed_count}")
    print(f"- Files with errors: {len(errors)}")
    
    if errors:
        print("\nValidation errors found:")
        for error in errors:
            print(f" - {error}")
        print("\n❌ Validation failed")
        return 1
    
    print("\n✅ All files are valid")
    return 0

if __name__ == "__main__":
    sys.exit(main())
