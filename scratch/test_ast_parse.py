import sys
sys.path.append(r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine")

from apcre_api import run_full_review

code = """# APCRE Coder Agent - Offline Fallback (Debugged & Fixed)
# Task: Create a Binary Search Tree (BST)

class TreeNode:
    def __init__(self, val):
        
        root.right = insert_node(root.right, val)
    return root

def inorder_traversal(root):
    if not root: return []
    return inorder_traversal(root.left) + [root.val] + inorder_traversal(root.right)
"""

issues = run_full_review(code, "test_tree_agent.py")
print("Issues found by run_full_review:")
for issue in issues:
    print(issue)
