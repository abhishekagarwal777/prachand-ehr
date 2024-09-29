class AuthorizationAspect(AnnotationAspect):
    def match_annotations(self):
        # Define that this aspect checks for 'authorization' annotations
        return ['ehrbase_authorization']

    def action(self, func, *args, **kwargs):
        print("Authorization aspect: Checking authorization before proceeding...")
        # Here, you could check if the user has the necessary permissions
        result = func(*args, **kwargs)  # Proceed with the original function
        print("Authorization aspect: Authorization check completed.")
        return result

authorization_aspect = AuthorizationAspect()

@apply_aspect(authorization_aspect)
def some_authorized_method():
    print("Executing method that requires authorization")

# When this method is called, authorization will be checked
some_authorized_method()


