from .libs import *
from profiles import models, engine


class ProfileAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.user = request.user
        self.profile = engine.ProfileEngine(self.user)
        self.method_prefix = 'update_'
    
    def get(self, request: Request, method: str) -> Response:
        return Response(
            engine.ProfileEngine.__dict__[method].fget(
                self.profile), status=status.HTTP_200_OK)
        
    def post(self, request: Request, method: str) -> Response:
        response = getattr(self.profile, self.method_prefix+method)(**request.data)
        if response is not None:
            return Response(response, status=status.HTTP_200_OK)
        return Response(dict(errors=self.profile.errors))
        
        
