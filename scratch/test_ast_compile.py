import ast

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

try:
    tree = ast.parse(code)
    print("ast.parse succeeded!")
    # Try compiling the AST to bytecode
    code_obj = compile(tree, 'test_tree_agent.py', 'exec')
    print("compile succeeded!")
except SyntaxError as e:
    print(f"compile failed with SyntaxError: {e}")
except Exception as e:
    print(f"compile failed with other error: {e}")
