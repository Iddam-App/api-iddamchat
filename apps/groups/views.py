from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.moderation.filter import check_and_flag

from .models import (
    Group, GroupJoinRequest, GroupMembership, GroupPost,
    Proposal, ProposalParticipant,
)
from .serializers import (
    GroupJoinRequestSerializer, GroupMembershipSerializer,
    GroupPostSerializer, GroupSerializer, ProposalSerializer,
)


class GroupListCreateView(generics.ListCreateAPIView):
    serializer_class = GroupSerializer
    filterset_fields = ['group_type', 'country']
    search_fields = ['name', 'description']

    def get_queryset(self):
        return Group.objects.filter(is_active=True)

    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)
        GroupMembership.objects.create(
            group=group, user=self.request.user, role='admin',
        )


class GroupDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = GroupSerializer
    queryset = Group.objects.filter(is_active=True)


class GroupMembersView(generics.ListAPIView):
    serializer_class = GroupMembershipSerializer

    def get_queryset(self):
        return GroupMembership.objects.filter(
            group_id=self.kwargs['pk'], is_active=True,
        ).select_related('user')


class JoinGroupView(APIView):
    def post(self, request, pk):
        group = generics.get_object_or_404(Group, pk=pk, is_active=True)
        if GroupMembership.objects.filter(
            group=group, user=request.user, is_active=True,
        ).exists():
            return Response(
                {'detail': 'Ya eres miembro.'}, status=status.HTTP_400_BAD_REQUEST,
            )
        if group.is_private:
            GroupJoinRequest.objects.get_or_create(
                group=group, user=request.user,
                defaults={'message': request.data.get('message', '')},
            )
            return Response({'detail': 'Solicitud enviada.'})
        GroupMembership.objects.create(group=group, user=request.user)
        return Response({'detail': 'Te uniste al grupo.'})


class LeaveGroupView(APIView):
    def post(self, request, pk):
        GroupMembership.objects.filter(
            group_id=pk, user=request.user,
        ).update(is_active=False)
        return Response({'detail': 'Saliste del grupo.'})


class GroupJoinRequestsView(generics.ListAPIView):
    serializer_class = GroupJoinRequestSerializer

    def get_queryset(self):
        return GroupJoinRequest.objects.filter(
            group_id=self.kwargs['pk'], status='pending',
        ).select_related('user')


class RespondJoinRequestView(APIView):
    def post(self, request, pk, action):
        jr = generics.get_object_or_404(GroupJoinRequest, pk=pk, status='pending')
        if action == 'accept':
            jr.status = 'accepted'
            jr.save(update_fields=['status'])
            GroupMembership.objects.get_or_create(group=jr.group, user=jr.user)
        elif action == 'reject':
            jr.status = 'rejected'
            jr.save(update_fields=['status'])
        return Response(GroupJoinRequestSerializer(jr).data)


class GroupPostListCreateView(generics.ListCreateAPIView):
    serializer_class = GroupPostSerializer

    def get_queryset(self):
        return GroupPost.objects.filter(
            group_id=self.kwargs['pk'],
        ).select_related('author')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content = serializer.validated_data.get('content', '')
        confirmed = request.data.get('confirmed', False)

        mod_result = check_and_flag(
            user=request.user, text=content,
            content_type='group_post', content_id=0, confirmed=confirmed,
        )

        if mod_result['severity'] == 'ban':
            return Response({
                'detail': mod_result['warning_message'],
                'severity': 'ban',
            }, status=status.HTTP_403_FORBIDDEN)

        if mod_result['needs_confirmation']:
            return Response({
                'detail': mod_result['warning_message'],
                'needs_confirmation': True,
                'severity': mod_result['severity'],
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        group = generics.get_object_or_404(Group, pk=self.kwargs['pk'])
        serializer.save(author=request.user, group=group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProposalListCreateView(generics.ListCreateAPIView):
    serializer_class = ProposalSerializer
    filterset_fields = ['proposal_type', 'is_open']

    def get_queryset(self):
        return Proposal.objects.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ProposalJoinView(APIView):
    def post(self, request, pk):
        proposal = generics.get_object_or_404(Proposal, pk=pk, is_open=True)
        _, created = ProposalParticipant.objects.get_or_create(
            proposal=proposal, user=request.user,
        )
        if not created:
            ProposalParticipant.objects.filter(
                proposal=proposal, user=request.user,
            ).delete()
            return Response({'participating': False})
        return Response({'participating': True})
