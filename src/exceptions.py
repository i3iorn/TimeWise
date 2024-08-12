class CategoryNotFoundException(Exception):
    """
    Exception raised for errors in the input category.
    """
    def __init__(self, category, message="Category not found."):
        self.category_name = category
        self.message = message
        super().__init__(self.message)