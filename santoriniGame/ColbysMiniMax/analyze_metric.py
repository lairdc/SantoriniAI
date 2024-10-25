import statistics

def analyze_metrics(file_name, x):
    metrics = {
        "piece_score": [],
        "a_score": [],
        "d_score": [],
        "r_score": []
    }
    with open(file_name, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "p_score" in line:
                value = float(line.split(":")[1].strip())
                # Ignore outliers for piece_score
                if -1000 < value < 1000:
                    metrics["piece_score"].append(value)
            elif "a_score" in line:
                metrics["a_score"].append(float(line.split(":")[1].strip()))
            elif "d_score" in line:
                metrics["d_score"].append(float(line.split(":")[1].strip()))
            elif "r_score" in line:
                metrics["r_score"].append(float(line.split(":")[1].strip()))

    # Function to calculate metrics
    def calc_stats(values):
        if len(values) == 0:
            return None, None, None, None, None
        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)
        median_val = statistics.median(values)
        count_in_range = len([v for v in values if -x <= v <= x])
        return min_val, max_val, avg_val, median_val, count_in_range

    # Display stats for each metric
    for metric, values in metrics.items():
        min_val, max_val, avg_val, median_val, count_in_range = calc_stats(values)
        print(f"{metric}:")
        print(f"  Min: {min_val}")
        print(f"  Max: {max_val}")
        print(f"  Average: {avg_val}")
        print(f"  Median: {median_val}")
        print(f"  Count within range -{x} to {x}: {count_in_range}")
        print()

# Example usage
analyze_metrics("score_metrics.txt", x=5)  # You can adjust `x` to whatever value you want.
