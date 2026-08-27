function editor() {
    return {
        // ---------- theme (shared, see theme.js) ----------
        ...themeMixin(),

        // ---------- state ----------
        tab: 'blog',
        writeKey: '',

        blog: { title: '', content_md: '' },
        project: { title: '', description: '', tech_stack: '', url: '' },

        blogStatus: '',
        blogStatusType: '',
        projectStatus: '',
        projectStatusType: '',

        blogPreview: '',
        projectPreview: '',

        posts: [],
        projectsList: [],
        manageError: null,

        editingBlogId: null,
        editingProjectId: null,

        init() {
            this.initTheme();
        },

        // ---------- computed ----------
        get canSubmitBlog() {
            return this.writeKey && this.blog.title && this.blog.content_md;
        },
        get canSubmitProject() {
            return this.writeKey && this.project.title;
        },

        // ---------- small helpers ----------

        /** Set the status message + type ('success' | 'error' | '') for a given form. */
        setStatus(form, message, type = '') {
            if (form === 'blog') {
                this.blogStatus = message;
                this.blogStatusType = type;
            } else {
                this.projectStatus = message;
                this.projectStatusType = type;
            }
        },

        /** Headers for a write-protected request. */
        authHeaders(extra = {}) {
            return { 'X-Write-Key': this.writeKey, ...extra };
        },

        /**
         * fetch() wrapper: parses JSON, and on failure pulls out `detail`
         * (or falls back to statusText) so callers don't repeat that logic.
         */
        async apiFetch(url, options = {}) {
            const res = await fetch(url, options);
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                const message = err.detail || res.statusText || `HTTP ${res.status}`;
                throw new Error(message);
            }
            return res.status === 204 ? null : res.json();
        },

        /** Markdown -> sanitized HTML, with a plain-text fallback if the CDN libs didn't load. */
        renderMarkdown(md) {
            if (!md) return '';
            try {
                const raw = typeof marked !== 'undefined'
                    ? marked.parse(md)
                    : md.replace(/\n/g, '<br/>');
                return typeof DOMPurify !== 'undefined' ? DOMPurify.sanitize(raw) : raw;
            } catch (e) {
                return md
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/\n/g, '<br/>');
            }
        },

        // ---------- manage tab ----------

        async loadManage() {
            this.manageError = null;
            try {
                const [bp, pp] = await Promise.all([fetch('/api/blog'), fetch('/api/project')]);

                if (bp.ok) {
                    this.posts = await bp.json();
                } else {
                    this.manageError = { ...this.manageError, posts: 'Failed to load posts' };
                }

                if (pp.ok) {
                    this.projectsList = await pp.json();
                } else {
                    this.manageError = { ...this.manageError, projects: 'Failed to load projects' };
                }
            } catch (e) {
                this.manageError = { posts: 'Network error', projects: 'Network error' };
            }
        },

        /** Refresh the manage lists, but only if that tab is currently visible. */
        async refreshManageIfVisible() {
            if (this.tab === 'manage') await this.loadManage();
        },

        // ---------- blog: edit / delete ----------

        async startEditBlog(post) {
            this.editingBlogId = post.id;
            this.blog.title = post.title;
            this.blog.content_md = '';
            this.tab = 'blog';

            try {
                const raw = await this.apiFetch(`/api/blog/${post.id}/raw`, {
                    headers: this.authHeaders(),
                });
                this.blog.content_md = raw.content_md || '';
            } catch (e) {
                this.setStatus('blog', 'Failed to load raw post (need write key)', 'error');
            }
        },

        async deleteBlog(id) {
            if (!confirm('Delete this post?')) return;
            try {
                await this.apiFetch(`/api/blog/${id}`, {
                    method: 'DELETE',
                    headers: this.authHeaders(),
                });
                this.setStatus('blog', 'Deleted', 'success');
                await this.loadManage();
            } catch (e) {
                this.setStatus('blog', 'Delete failed', 'error');
            }
        },

        // ---------- project: edit / delete ----------

        async startEditProject(pr) {
            this.editingProjectId = pr.id;
            try {
                const full = await this.apiFetch(`/api/project/${pr.slug}`);
                this.project.title = full.title;
                this.project.description = full.description || '';
                this.project.tech_stack = full.tech_stack || '';
                this.project.url = full.url || '';
                this.tab = 'project';
            } catch (e) {
                this.setStatus('project', 'Failed to load project for editing', 'error');
            }
        },

        async deleteProject(id) {
            if (!confirm('Delete this project?')) return;
            try {
                await this.apiFetch(`/api/project/${id}`, {
                    method: 'DELETE',
                    headers: this.authHeaders(),
                });
                this.setStatus('project', 'Deleted', 'success');
                await this.loadManage();
            } catch (e) {
                this.setStatus('project', 'Delete failed', 'error');
            }
        },

        // ---------- blog: create / update ----------

        async createBlog() {
            this.setStatus('blog', 'Publishing...');

            const isEdit = Boolean(this.editingBlogId);
            const url = isEdit ? `/api/blog/${this.editingBlogId}` : '/api/blog';
            const method = isEdit ? 'PUT' : 'POST';

            try {
                const data = await this.apiFetch(url, {
                    method,
                    headers: this.authHeaders({ 'Content-Type': 'application/json' }),
                    body: JSON.stringify({ title: this.blog.title, content_md: this.blog.content_md }),
                });

                this.setStatus('blog', (isEdit ? 'Updated ' : 'Published! View at /blog/') + data.slug, 'success');

                this.blog = { title: '', content_md: '' };
                this.blogPreview = '';
                this.editingBlogId = null;
                this.tab = 'blog';
            } catch (e) {
                this.setStatus('blog', 'Error: ' + e.message, 'error');
            } finally {
                await this.refreshManageIfVisible();
            }
        },

        async previewBlog() {
            this.blogPreview = this.renderMarkdown(this.blog.content_md);
        },

        // ---------- project: create / update ----------

        async createProject() {
            this.setStatus('project', 'Creating project...');

            const techs = (this.project.tech_stack || '')
                .split(',')
                .map(s => s.trim())
                .filter(Boolean)
                .join(', ');

            let url = this.project.url || null;
            if (url) {
                try {
                    new URL(url);
                } catch (e) {
                    this.setStatus('project', 'Error: invalid URL', 'error');
                    return;
                }
            }

            const payload = {
                title: this.project.title,
                description: this.project.description || null,
                tech_stack: techs || null,
                url,
            };

            const isEdit = Boolean(this.editingProjectId);
            const endpoint = isEdit ? `/api/project/${this.editingProjectId}` : '/api/project';
            const method = isEdit ? 'PUT' : 'POST';

            try {
                const data = await this.apiFetch(endpoint, {
                    method,
                    headers: this.authHeaders({ 'Content-Type': 'application/json' }),
                    body: JSON.stringify(payload),
                });

                this.setStatus('project', (isEdit ? 'Updated ' : 'Created! View at /project/') + data.slug, 'success');

                this.project = { title: '', description: '', tech_stack: '', url: '' };
                this.editingProjectId = null;
            } catch (e) {
                this.setStatus('project', 'Error: ' + e.message, 'error');
            } finally {
                await this.refreshManageIfVisible();
            }
        },

        async previewProject() {
            this.projectPreview = this.renderMarkdown(this.project.description);
        },
    };
}
