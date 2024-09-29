from typing import Callable, Optional, TypeVar

# Define type variables for generic functions
IN = TypeVar('IN')
OUT = TypeVar('OUT')

class ExtensionPointHelper:
    """
    Extension Point Helper for handling operations before and after a chain of functions.
    """

    @staticmethod
    def before(input: IN, chain: Callable[[IN], OUT], 
               before: Optional[Callable[[IN], IN]]) -> OUT:
        """
        Applies "before" to the input, uses the result to proceed with the chain and returns the result of the chain.
        Providing None for "before" is allowed and will cause the step to be skipped.

        Args:
            input: Input to use.
            chain: Call chain function.
            before: Function applied to input before proceeding with the chain, Optional/nullable.

        Returns:
            Result of chain(before(input)).
        """
        return ExtensionPointHelper.before_and_after(input, chain, before, None)

    @staticmethod
    def after(input: IN, chain: Callable[[IN], OUT], 
              after: Optional[Callable[[OUT], OUT]]) -> OUT:
        """
        Proceeds with the chain and returns the result of the chain after applying "after" to it.
        Providing None for "after" is allowed and will cause the step to be skipped.

        Args:
            input: Input to use.
            chain: Call chain function.
            after: Function applied to the result of proceeding with the chain, Optional/nullable.

        Returns:
            Result of after(chain(input)).
        """
        return ExtensionPointHelper.before_and_after(input, chain, None, after)

    @staticmethod
    def before_and_after(input: IN, chain: Callable[[IN], OUT], 
                         before: Optional[Callable[[IN], IN]], 
                         after: Optional[Callable[[OUT], OUT]]) -> OUT:
        """
        Applies "before" to the input, uses the result to proceed with the chain and returns the result of the chain
        after applying "after" to it.
        Providing None for "before" or "after" is allowed and will cause the step to be skipped.

        Args:
            input: Input to use.
            chain: Call chain function.
            before: Function applied to input before proceeding with the chain, Optional/nullable.
            after: Function applied to the result of proceeding with the chain, Optional/nullable.

        Returns:
            Result of after(chain(before(input))).
        """
        # Apply the before function if it's provided, otherwise use the original input
        if before is not None:
            input = before(input)

        # Call the chain function with the modified or original input
        result = chain(input)

        # Apply the after function if it's provided
        if after is not None:
            result = after(result)

        return result
