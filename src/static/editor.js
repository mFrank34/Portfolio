function editor() {
    return {
        tab: 'blog',
        writeKey: '',
        blog: { title: '', content_md: '' },
        project: { title: '', description: '', tech_stack: '', url: '' },
        blogStatus: '',
        projectStatus: '',
        blogStatusType: '',
        projectStatusType: '',
        blogPreview: '',
        projectPreview: '',
        posts: [],
        projectsList: [],
        manageError: null,
        editingBlogId: null,
        editingProjectId: null,

        get canSubmitBlog() {
            return this.writeKey && this.blog.title && this.blog.content_md;
        },
        get canSubmitProject() {
            return this.writeKey && this.project.title;
        },

        async loadManage() {
            this.manageError = null;
            try {
                const [bp, pp] = await Promise.all([fetch('/api/blog'), fetch('/api/project')]);
                if (!bp.ok) { this.manageError = this.manageError || {}; this.manageError.posts = 'Failed to load posts'; } else { this.posts = await bp.json(); }
                if (!pp.ok) { this.manageError = this.manageError || {}; this.manageError.projects = 'Failed to load projects'; } else { this.projectsList = await pp.json(); }
            } catch (e) {
                this.manageError = { posts: 'Network error', projects: 'Network error' };
            }
        },

        startEditBlog(post) {
            this.editingBlogId = post.id;
            this.blog.title = post.title;
            this.blog.content_md = '';
            this.tab = 'blog';
            (async () => {
                try {
                    const res = await fetch('/api/blog/' + post.id + '/raw', { headers: { 'X-Write-Key': this.writeKey } });
                    if (res.ok) {
                        const raw = await res.json();
                        this.blog.content_md = raw.content_md || '';
                    } else {
                        this.blogStatus = 'Failed to load raw post (need write key)';
                        this.blogStatusType = 'error';
                    }
                } catch (e) {
                    this.blogStatus = 'Network error: ' + e.message;
                    this.blogStatusType = 'error';
                }
            })();
        },


        startEditProject(pr) {
            this.editingProjectId = pr.id;
            (async () => {
                try {
                    const res = await fetch('/api/project/' + pr.slug);
                    if (res.ok) {
                        const full = await res.json();
                        this.project.title = full.title;
                        this.project.description = full.description || '';
                        this.project.tech_stack = full.tech_stack || '';
                        this.project.url = full.url || '';
                        this.tab = 'project';
                    } else {
                        this.projectStatus = 'Failed to load project for editing';
                        this.projectStatusType = 'error';
                    }
                } catch (e) {
                    this.projectStatus = 'Network error: ' + e.message;
                    this.projectStatusType = 'error';
                }
            })();
        },

        async deleteBlog(id) {
            if (!confirm('Delete this post?')) return;
            try {
                const res = await fetch('/api/blog/' + id, { method: 'DELETE', headers: { 'X-Write-Key': this.writeKey } });
                if (!res.ok) { this.blogStatus = 'Delete failed'; this.blogStatusType = 'error'; return; }
                this.blogStatus = 'Deleted'; this.blogStatusType = 'success';
                await this.loadManage();
            } catch (e) {
                this.blogStatus = 'Network error: ' + e.message; this.blogStatusType = 'error';
            }
        },

        async deleteProject(id) {
            if (!confirm('Delete this project?')) return;
            try {
                const res = await fetch('/api/project/' + id, { method: 'DELETE', headers: { 'X-Write-Key': this.writeKey } });
                if (!res.ok) { this.projectStatus = 'Delete failed'; this.projectStatusType = 'error'; return; }
                this.projectStatus = 'Deleted'; this.projectStatusType = 'success';
                await this.loadManage();
            } catch (e) {
                this.projectStatus = 'Network error: ' + e.message; this.projectStatusType = 'error';
            }
        },

        async createBlog() {
            // If editing, perform PUT; otherwise create new
            this.blogStatus = 'Publishing...';
            this.blogStatusType = '';
            try {
                let res;
                if (this.editingBlogId) {
                    res = await fetch('/api/blog/' + this.editingBlogId, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json', 'X-Write-Key': this.writeKey },
                        body: JSON.stringify({ title: this.blog.title, content_md: this.blog.content_md }),
                    });
                } else {
                    res = await fetch('/api/blog', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'X-Write-Key': this.writeKey },
                        body: JSON.stringify({ title: this.blog.title, content_md: this.blog.content_md }),
                    });
                }
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    this.blogStatus = 'Error: ' + (err.detail || res.statusText || res.status);
                    this.blogStatusType = 'error';
                    return;
                }
                const data = await res.json();
                this.blogStatus = (this.editingBlogId ? 'Updated ' : 'Published! View at /blog/') + data.slug;
                this.blogStatusType = 'success';
                // clear form but keep key
                this.blog = { title: '', content_md: '' };
                this.blogPreview = '';
                this.editingBlogId = null;
                this.tab = 'blog';
                // refresh manage lists if visible
                if (this.tab === 'manage') { await this.loadManage(); }
            } catch (e) {
                this.blogStatus = 'Network error: ' + e.message;
                this.blogStatusType = 'error';
            } finally {
                // if in manage view, refresh lists
                if (this.tab === 'manage') { await this.loadManage(); }
            }
        },

        async previewBlog() {
            const md = this.blog.content_md || '';
            if (!md) { this.blogPreview = ''; return; }
            try {
                // use marked + DOMPurify from CDN
                const raw = (typeof marked !== 'undefined') ? marked.parse(md) : md.replace(/\n/g, '<br/>');
                const clean = (typeof DOMPurify !== 'undefined') ? DOMPurify.sanitize(raw) : raw;
                this.blogPreview = clean;
            } catch (e) {
                // Fallback: escape HTML and show plain text
                this.blogPreview = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br/>');
            }
        },

        async previewProject() {
            const md = this.project.description || '';
            if (!md) { this.projectPreview = ''; return; }
            try {
                const raw = (typeof marked !== 'undefined') ? marked.parse(md) : md.replace(/\n/g, '<br/>');
                const clean = (typeof DOMPurify !== 'undefined') ? DOMPurify.sanitize(raw) : raw;
                this.projectPreview = clean;
            } catch (e) {
                this.projectPreview = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br/>');
            }
        },

        async createProject() {
            this.projectStatus = 'Creating project...';
            this.projectStatusType = '';
            try {
                // normalize tech stack into a comma-separated, trimmed string
                const techs = (this.project.tech_stack || '').split(',').map(s => s.trim()).filter(Boolean).join(', ');
                // basic URL validation
                let url = this.project.url || null;
                if (url) {
                    try { new URL(url); } catch (e) { this.projectStatus = 'Error: invalid URL'; this.projectStatusType = 'error'; return; }
                }
                const payload = {
                    title: this.project.title,
                    description: this.project.description || null,
                    tech_stack: techs || null,
                    url: url || null,
                };
                let res;
                if (this.editingProjectId) {
                    res = await fetch('/api/project/' + this.editingProjectId, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json', 'X-Write-Key': this.writeKey },
                        body: JSON.stringify({ writeKey: this.writeKey, ...payload }),
                    });
                } else {
                    res = await fetch('/api/project', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'X-Write-Key': this.writeKey },
                        body: JSON.stringify(payload),
                    });
                }
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    this.projectStatus = 'Error: ' + (err.detail || res.statusText || res.status);
                    this.projectStatusType = 'error';
                    return;
                }
                const data = await res.json();
                this.projectStatus = (this.editingProjectId ? 'Updated ' : 'Created! View at /project/') + data.slug;
                this.projectStatusType = 'success';
                this.project = { title: '', description: '', tech_stack: '', url: '' };
                this.editingProjectId = null;
                if (this.tab === 'manage') { await this.loadManage(); }
            } catch (e) {
                this.projectStatus = 'Network error: ' + e.message;
                this.projectStatusType = 'error';
            } finally {
                if (this.tab === 'manage') { await this.loadManage(); }
            }
        }
    };
}