import os
import datetime

def get_next_output_dir(base_path="result"):
    """
    Determines the next available output directory based on the current date.
    Format: YYYY-MM-DD, YYYY-MM-DD(1), YYYY-MM-DD(2), ...
    """
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    base_dir = os.path.join(base_path, today)
    
    if not os.path.exists(base_dir):
        return base_dir
    
    counter = 1
    while True:
        new_dir = f"{base_dir}({counter})"
        if not os.path.exists(new_dir):
            return new_dir
        counter += 1

def create_output_dir(base_path="result"):
    """
    Creates and returns the next available output directory.
    """
    target_dir = get_next_output_dir(base_path)
    os.makedirs(target_dir, exist_ok=True)
    print(f"Created output directory: {target_dir}")
    return target_dir

if __name__ == "__main__":
    # Test execution
    create_output_dir()
