#!/bin/bash
# Chained hook - runs existing hook then HtmlGraph hook

if [ -f ".git/hooks/post-commit.existing" ]; then
  ".git/hooks/post-commit.existing" || exit $?
fi

if [ -f ".htmlgraph/hooks/post-commit.sh" ]; then
  ".htmlgraph/hooks/post-commit.sh" || true
fi
