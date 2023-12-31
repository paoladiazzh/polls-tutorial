from typing import Any, Dict
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.contrib.auth.decorators import login_required

from .models import Choice, Question, Vote


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"
    context_object_name = "question"
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        question = self.get_object()
        choices = question.choice_set.all()
        data = [{'choice_text': choice.choice_text, 'votes': choice.votes} for choice in choices]
        context['data'] = data
        context['question'] = question
        return context

@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        user = request.user
        selected_choice.votes += 1
        selected_choice.save()
        vote = Vote.objects.create(user=user, choice=selected_choice)
        return HttpResponseRedirect(reverse("polls:results", args=(question_id,)))

