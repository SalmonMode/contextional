from __future__ import absolute_import

import os

from nose.plugins.base import Plugin
from nose.plugins.collect import CollectOnly


class NoseDryRun(CollectOnly):
    """Modified CollectOnly that can handle Contextional tests."""

    name = "contextional-nose-dry-run"

    def options(self, parser, env=os.environ):
        Plugin.options(self, parser, env=env)

    def configure(self, options, conf):
        """Remove the original CollectOnly plugin, so only this one runs.

        This removes the original CollectOnly plugin from the conf's list of
        plugins, so that this plugin and the original CollectOnly plugin don't
        conflict with each other. The original CollectOnly plugin is kept so
        that it can be used later to preserve the original behavior.
        """
        super(NoseDryRun, self).configure(options, conf)
        if not self.enabled:
            return
        for plugin in self.conf.plugins.plugins:
            if isinstance(plugin, CollectOnly):
                if not isinstance(plugin, NoseDryRun):
                    self.old_collect_only = plugin
                    self.conf.plugins.plugins.remove(plugin)

    def prepareTestCase(self, test):
        """Replace actual test with dummy that always passes.

        Replace actual test with dummy that always passes and spits out all the
        group/fixture descriptions properly.
        """
        test.test._dry_run = True
        default_run = self.old_collect_only.prepareTestCase(test)

        def run(result):
            # test.test._result = result
            test.test._dry_run_setup(result)
            default_run(result)
            test.test._dry_run_teardown()

        return run
