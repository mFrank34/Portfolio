function editor() {
    return {
        ...themeMixin(),

        section: 'page',

        page: { hero_title: '', hero_subtitle: '', content: '' },
        pageExists: false,
        pageStatus: '', pageStatusType: '', pagePreview: '',

        blog: { title: '', content_md: '' },
        blogStatus: '', blogStatusType: '', blogPreview: '',
        editingBlogId: null,
        posts: [],

        project: { title: '', description: '', tech_stack: '', url: '' },
        projectStatus: '', projectStatusType: '',
        editingProjectId: null,
        projectsList: [],

        skills: [],
        newSkill: '', newSkillCategory: '', newSkillLevel: '',
        editingSkillId: null,
        skillsStatus: '', skillsStatusType: '',

        socials: [],
        newSite: '', newLink: '', newIcon: '',
        editingSocialId: null,
        socialsStatus: '', socialsStatusType: '',

        async init() {
            this.initTheme();
            // Confirm session is valid before showing the dashboard
            try {
                await this.apiFetch('/auth/me');
            } catch (e) {
                return; // apiFetch already redirects to /login on 401
            }
            await Promise.all([
                this.loadPage(),
                this.loadBlogs(),
                this.loadProjects(),
                this.loadSkills(),
                this.loadSocials(),
            ]);
        },

        get canSubmitBlog() {
            return this.blog.title && this.blog.content_md;
        },
        get canSubmitProject() {
            return this.project.title;
        },
        get canSubmitPage() {
            return this.page.hero_title && this.page.hero_subtitle && this.page.content;
        },

        setStatus(form, message, type = '') {
            this[form + 'Status'] = message;
            this[form + 'StatusType'] = type;
        },

        async logout() {
            try {
                await fetch('/auth/logout', { method: 'POST' }); // with /auth prefix
            } catch (e) { }
            window.location.href = '/login';
        },

        async apiFetch(url, options = {}) {
            const res = await fetch(url, options);
            if (res.status === 401) {
                window.location.href = '/login';
                throw new Error('Not authenticated');
            }
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || res.statusText || `HTTP ${res.status}`);
            }
            return res.status === 204 ? null : res.json();
        },

        renderMarkdown(md) {
            if (!md) return '';
            try {
                const raw = marked.parse(md);
                return DOMPurify.sanitize(raw);
            } catch (e) {
                return md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            }
        },

        // ---------- page ----------
        // Inside your editor.js component

        async loadPage() {
            // Use the /raw endpoint so the textarea gets raw Markdown, not rendered HTML
            const res = await fetch('/api/page/raw');
            if (res.ok) {
                this.page = await res.json();
            }
        },

        async savePage() {
            // Use PUT because page ID 1 already exists (POST creates a new one and causes the 409 error)
            const res = await fetch('/api/page', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    hero_title: this.page.hero_title,
                    hero_subtitle: this.page.hero_subtitle,
                    content: this.page.content
                })
            });

            if (res.ok) {
                this.pageStatus = 'Saved successfully!';
                this.pageStatusType = 'success';
            } else {
                const err = await res.json();
                this.pageStatus = err.detail || 'Error saving page';
                this.pageStatusType = 'error';
            }
        },

        // ---------- blog ----------
        async loadBlogs() {
            this.posts = await this.apiFetch('/api/blog').catch(() => []);
        },
        async startEditBlog(post) {
            this.editingBlogId = post.id;
            this.blog.title = post.title;
            try {
                const raw = await this.apiFetch(`/api/blog/${post.id}/raw`);
                this.blog.content_md = raw.content_md || '';
            } catch (e) {
                this.setStatus('blog', 'Failed to load post content', 'error');
            }
        },
        cancelEditBlog() {
            this.editingBlogId = null;
            this.blog = { title: '', content_md: '' };
            this.blogPreview = '';
        },
        async createBlog() {
            this.setStatus('blog', 'Saving...');
            const isEdit = Boolean(this.editingBlogId);
            try {
                const data = await this.apiFetch(isEdit ? `/api/blog/${this.editingBlogId}` : '/api/blog', {
                    method: isEdit ? 'PUT' : 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.blog),
                });
                this.setStatus('blog', (isEdit ? 'Updated ' : 'Published: ') + data.slug, 'success');
                this.cancelEditBlog();
                await this.loadBlogs();
            } catch (e) {
                this.setStatus('blog', 'Error: ' + e.message, 'error');
            }
        },
        async deleteBlog(id) {
            if (!confirm('Delete this post?')) return;
            try {
                await this.apiFetch(`/api/blog/${id}`, { method: 'DELETE' });
                await this.loadBlogs();
            } catch (e) {
                this.setStatus('blog', 'Delete failed: ' + e.message, 'error');
            }
        },

        // ---------- project ----------
        async loadProjects() {
            this.projectsList = await this.apiFetch('/api/project').catch(() => []);
        },
        async startEditProject(pr) {
            this.editingProjectId = pr.id;
            this.project = {
                title: pr.title,
                description: pr.description || '',
                tech_stack: pr.tech_stack || '',
                url: pr.url || '',
            };
        },
        cancelEditProject() {
            this.editingProjectId = null;
            this.project = { title: '', description: '', tech_stack: '', url: '' };
        },
        async createProject() {
            this.setStatus('project', 'Saving...');
            if (this.project.url) {
                try { new URL(this.project.url); }
                catch (e) { this.setStatus('project', 'Error: invalid URL', 'error'); return; }
            }
            const isEdit = Boolean(this.editingProjectId);
            try {
                const data = await this.apiFetch(isEdit ? `/api/project/${this.editingProjectId}` : '/api/project', {
                    method: isEdit ? 'PUT' : 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.project),
                });
                this.setStatus('project', (isEdit ? 'Updated ' : 'Created: ') + data.slug, 'success');
                this.cancelEditProject();
                await this.loadProjects();
            } catch (e) {
                this.setStatus('project', 'Error: ' + e.message, 'error');
            }
        },
        async deleteProject(id) {
            if (!confirm('Delete this project?')) return;
            try {
                await this.apiFetch(`/api/project/${id}`, { method: 'DELETE' });
                await this.loadProjects();
            } catch (e) {
                this.setStatus('project', 'Delete failed: ' + e.message, 'error');
            }
        },

        // ---------- skills ----------
        async loadSkills() {
            this.skills = await this.apiFetch('/api/skills').catch(() => []);
        },
        startEditSkill(skill) {
            this.editingSkillId = skill.id;
            this.newSkill = skill.name;
            this.newSkillCategory = skill.category || '';
            this.newSkillLevel = skill.level || '';
        },
        cancelEditSkill() {
            this.editingSkillId = null;
            this.newSkill = ''; this.newSkillCategory = ''; this.newSkillLevel = '';
        },
        async saveSkill() {
            if (!this.newSkill.trim()) return;
            const isEdit = Boolean(this.editingSkillId);
            try {
                await this.apiFetch(isEdit ? `/api/skills/${this.editingSkillId}` : '/api/skills', {
                    method: isEdit ? 'PUT' : 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: this.newSkill,
                        category: this.newSkillCategory || null,
                        level: this.newSkillLevel || null,
                    }),
                });
                this.setStatus('skills', isEdit ? 'Updated' : 'Added', 'success');
                this.cancelEditSkill();
                await this.loadSkills();
            } catch (e) {
                this.setStatus('skills', 'Error: ' + e.message, 'error');
            }
        },
        async deleteSkill(id) {
            if (!confirm('Delete this skill?')) return;
            try {
                await this.apiFetch(`/api/skills/${id}`, { method: 'DELETE' });
                await this.loadSkills();
            } catch (e) {
                this.setStatus('skills', 'Delete failed: ' + e.message, 'error');
            }
        },

        // ---------- socials ----------
        async loadSocials() {
            this.socials = await this.apiFetch('/api/socials').catch(() => []);
        },
        startEditSocial(social) {
            this.editingSocialId = social.id;
            this.newSite = social.site;
            this.newLink = social.link;
            this.newIcon = social.icon;
        },
        cancelEditSocial() {
            this.editingSocialId = null;
            this.newSite = ''; this.newLink = ''; this.newIcon = '';
        },
        async saveSocial() {
            if (!this.newSite.trim() || !this.newLink.trim() || !this.newIcon.trim()) return;
            const isEdit = Boolean(this.editingSocialId);
            try {
                await this.apiFetch(isEdit ? `/api/socials/${this.editingSocialId}` : '/api/socials', {
                    method: isEdit ? 'PUT' : 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ site: this.newSite, link: this.newLink, icon: this.newIcon }),
                });
                this.setStatus('socials', isEdit ? 'Updated' : 'Added', 'success');
                this.cancelEditSocial();
                await this.loadSocials();
            } catch (e) {
                this.setStatus('socials', 'Error: ' + e.message, 'error');
            }
        },
        async deleteSocial(id) {
            if (!confirm('Delete this social link?')) return;
            try {
                await this.apiFetch(`/api/socials/${id}`, { method: 'DELETE' });
                await this.loadSocials();
            } catch (e) {
                this.setStatus('socials', 'Delete failed: ' + e.message, 'error');
            }
        },
    };
}