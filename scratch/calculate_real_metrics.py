# Calculate exact metrics from the confusion matrix
import numpy as np

classes = [
    "API Design Problems",
    "Architectural Violations",
    "Clean Code",
    "Code Smells",
    "Concurrency Issues",
    "Design Pattern Violations",
    "Error Handling Problems",
    "High Coupling"
]

# Confusion matrix rows are actual, columns are predicted
matrix = np.array([
    [1960, 10,  5,  8, 12,  3,  1,  1],
    [15, 430, 25,  5,  5, 10,  2,  8],
    [10, 30, 420, 15,  5,  5, 10,  5],
    [12,  5, 15, 910, 20, 15, 11, 12],
    [25,  5,  5, 15, 1920, 10, 15,  5],
    [5, 15, 10, 10, 20, 1410, 10, 20],
    [8,  2,  8, 12, 15,  5, 960, 10],
    [10,  8,  5, 18, 10, 25, 12, 1412]
])

total_actual = matrix.sum(axis=1)
total_predicted = matrix.sum(axis=0)
tp = np.diag(matrix)

print(f"Total instances: {matrix.sum()}")
print(f"Total TP: {tp.sum()}")
print(f"Micro-averaged accuracy: {tp.sum() / matrix.sum() * 100:.4f}%")

print("\nClass-level Metrics:")
print(f"{'Class Name':<30} | {'Precision':<9} | {'Recall':<9} | {'F1-Score':<9}")
print("-" * 66)
for i, name in enumerate(classes):
    precision = tp[i] / total_predicted[i]
    recall = tp[i] / total_actual[i]
    f1 = 2 * (precision * recall) / (precision + recall)
    print(f"{name:<30} | {precision:.4f}    | {recall:.4f} | {f1:.4f}")
