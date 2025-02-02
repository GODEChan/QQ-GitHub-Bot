#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-11 16:57:04
@LastEditors    : yanyongyu
@LastEditTime   : 2021-09-12 01:20:35
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import datetime
from typing import List, Union, Optional

from pydantic import BaseModel as _BaseModel

from .user import User
from .label import Label
from .comment import Comment
from .pull_request import PullRequest
from . import BaseModel, PaginatedList
from .timeline import (
    TimelineEvent,
    TimelineEventClosed,
    TimelineEventMerged,
    TimelineEventLabeled,
    TimelineEventRenamed,
    TimelineEventAssigned,
    TimelineEventCommited,
    TimelineEventDeployed,
    TimelineEventReviewed,
    TimelineEventCommented,
    TimelineEventMentioned,
    TimelineEventUnlabeled,
    TimelineEventMilestoned,
    TimelineEventReferenced,
    TimelineEventSubscribed,
    TimelineEventForcePushed,
    TimelineEventHeadDeleted,
    TimelineEventDemilestoned,
    TimelineEventUnsubscribed,
    TimelineEventReviewRemoved,
    TimelineEventAddedToProject,
    TimelineEventCommentDeleted,
    TimelineEventReviewDismissed,
    TimelineEventReviewRequested,
    TimelineEventRemovedFromProject,
    TimelineEventMovedColumnsInProject,
)


class IssuePullRequest(_BaseModel):
    url: str
    html_url: str
    diff_url: str
    patch_url: str


class Issue(BaseModel):
    id: int
    node_id: str
    url: str
    repository_url: str
    labels_url: str
    comments_url: str
    events_url: str
    timeline_url: str
    html_url: str
    number: int
    state: str
    title: str
    body: Optional[str]
    body_text: Optional[str]
    body_html: Optional[str]
    user: User
    labels: List[Label]
    assignee: Optional[User]
    assignees: List[User]
    # milestone: Optional[Milestone]
    locked: bool
    active_lock_reason: Optional[str]
    comments: int
    pull_request: Optional[IssuePullRequest]
    closed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    closed_by: Optional[User]
    author_association: str

    @property
    def is_pull_request(self) -> bool:
        return bool(self.pull_request)

    async def get_comments(self) -> PaginatedList[Comment]:
        """
        GET /repo/:full_name/issues/:number/comments

        https://docs.github.com/en/rest/reference/issues#list-issue-comments
        """
        headers = {"Accept": "application/vnd.github.v3.full+json"}
        return PaginatedList(
            Comment, self.requester, "GET", self.comments_url, headers=headers
        )

    async def get_timeline(self) -> PaginatedList[TimelineEvent]:
        """
        GET /repo/:full_name/issues/:number/timeline

        https://docs.github.com/en/rest/reference/issues#list-timeline-events-for-an-issue
        """
        headers = {
            "Accept": "application/vnd.github.mockingbird-preview.full+json, "
            "application/vnd.github.starfox-preview+json"
        }
        return PaginatedList(
            Union[
                TimelineEventCommited,
                TimelineEventForcePushed,
                TimelineEventHeadDeleted,
                TimelineEventReferenced,
                TimelineEventCommented,
                TimelineEventCommentDeleted,
                TimelineEventAssigned,
                TimelineEventMentioned,
                TimelineEventSubscribed,
                TimelineEventUnsubscribed,
                TimelineEventReviewed,
                TimelineEventReviewRequested,
                TimelineEventReviewRemoved,
                TimelineEventReviewDismissed,
                TimelineEventRenamed,
                TimelineEventLabeled,
                TimelineEventUnlabeled,
                TimelineEventMerged,
                TimelineEventDeployed,
                TimelineEventClosed,
                TimelineEventAddedToProject,
                TimelineEventMovedColumnsInProject,
                TimelineEventRemovedFromProject,
                TimelineEventMilestoned,
                TimelineEventDemilestoned,
                TimelineEvent,
            ],
            self.requester,
            "GET",
            self.timeline_url,
            headers=headers,
        )

    async def get_pull_request(self) -> PullRequest:
        """
        GET /repo/:full_name/pull/:number
        """
        if not self.pull_request:
            raise RuntimeError(f"Issue {self.number} is not a pull request")

        headers = {"Accept": "application/vnd.github.v3.full+json"}
        response = await self.requester.request(
            "GET", self.pull_request.url, headers=headers
        )
        return PullRequest.parse_obj(
            {"requester": self.requester, **response.json()}
        )

    async def get_diff(self) -> str:
        """
        GET /repo/:full_name/pull/:number.diff
        """
        if not self.pull_request:
            raise RuntimeError(f"Issue {self.number} is not a pull request")

        response = await self.requester.request(
            "GET", self.pull_request.diff_url
        )
        return response.text
