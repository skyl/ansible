from test.TestRunner import BaseRunnerTestCase


class GitTestCase(BaseRunnerTestCase):

    def setUp(self):
        super(GitTestCase, self).setUp()
        self.repo = "/tmp/gitdemo_repo"
        self.repo_chdir = 'chdir=%s' % self.repo
        self.dest = "/tmp/gitdemo_dest"
        self.dest_chdir = 'chdir=%s' % self.dest
        # ensure these paths are blank
        self._run('file', ['path=%s' % self.repo, 'state=absent'])
        self._run('file', ['path=%s' % self.dest, 'state=absent'])
        # start repo in /tmp/gitdemo
        self._run('command', ['git init gitdemo_repo', 'chdir=/tmp'])
        self._run('command', ['touch a', self.repo_chdir])
        self._run('command', ['git add *', self.repo_chdir])
        self._run('command', ['git commit -m "test commit 1"', self.repo_chdir])
        self._run('command', ['touch b', self.repo_chdir])
        self._run('command', ['git add *', self.repo_chdir])
        self._run('command', ['git commit -m "test commit 2"', self.repo_chdir])
        self.git_options = ["repo=file://%s" % self.repo, "dest=%s" % self.dest]
        result = self._run('git', self.git_options)
        self.assert_(result['changed'])

    def tearDown(self):
        super(GitTestCase, self).tearDown()
        #self._run('file', ['path=%s' % self.repo, 'state=absent'])
        #self._run('file', ['path=%s' % self.dest, 'state=absent'])

    def test_git_clone_idempotent(self):
        result = self._run('git', self.git_options)
        self.assert_(not result['changed'])

    def test_git_force(self):
        # remove file
        self._run('file', ['path=%s/a' % self.dest, 'state=absent'])
        # fail with local changes and no force
        result = self._run('git', self.git_options + ["force=no"])
        self.assert_(result['failed'])
        # test the force option when set
        result = self._run('git', self.git_options + ["force=yes"])
        self.assert_(result['changed'])

    def test_remote(self):
        # remove destination
        self._run('file', ['path=%s' % self.dest, 'state=absent'])
        self._run('git', self.git_options + ["remote=mine"])
        mine = self._run('command', ['git remote', self.dest_chdir])['stdout']
        self.assertEqual("mine", mine)

    def test_executable(self):
        res = self._run('git', self.git_options + ["executable=/surely/not"])
        msg = "/surely/not: No such file or directory"
        self.assertIn(msg, res['msg'])

    def test_git_depth(self):
        from nose.plugins.skip import SkipTest
        raise SkipTest("git does not respect --depth on a local repo?")
        # remove dest
        self._run('file', ['path=%s' % self.dest, 'state=absent'])
        # git ignores depth on a local repo, it seems
        res = self._run('git', self.git_options + ["depth=1"])
        # this actually works but requires network
        #res = self._run('git', ["repo=https://github.com/ansible/awx-cli", "dest=/tmp/gitdemo_dest"] + ["depth=1"])
        res = self._run('command', ['git rev-list HEAD --count', self.dest_chdir])
        self.assertEqual(res['stdout'], '1')
