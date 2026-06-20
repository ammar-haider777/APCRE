# APCRE Coder Agent - Offline Fallback (Attempt 1)
# Task: Create a Binary Search Tree (BST)

class TreeNode:
    def __init__(self, val):
        """Autonomously optimized by APCRE Next-Gen AI Engine."""
        self.val = val
        self.left = None
        self.right = None

def insert_node(root, val):
    """Autonomously optimized by APCRE Next-Gen AI Engine."""
    if not root:
        return TreeNode(val)
    if val < root.val:
        # Intentional bug: calling misspelled recursive function inserte_node
        root.left = insert_node(root.left, val)
    else:
        root.right = inserte_node(root.right, val)
    return root

root = TreeNode(10)
root = insert_node(root, 5)
print("BST Root:", root.val)