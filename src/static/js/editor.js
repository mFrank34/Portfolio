function editor() {
    return {
        // ---------- theme (shared, see theme.js) ----------
        ...themeMixin(),

        // ---------- state ----------
        tab: 'page',
        writeKey: '',

        page: { hero_title: '', hero_subtitle: '', content: '' },
        pageExists: false,
        pageStatus: '',
        pageStatusType: '',
        pagePreview: '',

        blog: { title: '', content_md: '' },
        project: { title: '', description: '', tech_stack: '', url: '' },

        // Skills state matching SkillIn schema
        skills: [],
        newSkill: '',
        newSkillCategory: '',
        newSkillLevel: '',
        editingSkillId: null,

        // Socials state matching SocialIn schema
        socials: [],
        newSite: '',
        newLink: '',
        newIcon: '',
        editingSocialId: null,

        blogStatus: '',
        blogStatusType: '',
        projectStatus: '',
        projectStatusType: '',
        skillsStatus: '',
        skillsStatusType: '',
        socialsStatus: '',
        socialsStatusType: '',

        blogPreview: '',
        projectPreview: '',

        posts: [],
        projectsList: [],
        manageError: null,

        editingBlogId: null,
        editingProjectId: null,

        init() {
            this.initTheme();
            this.loadSkills();
            this.loadSocials();
            this.loadPage();
        },

        // ---------- computed ----------
        get canSubmitBlog() {
            return this.writeKey && this.blog.title && this.blog.content_md;
        },
        get canSubmitProject() {
            return this.writeKey && this.project.title;
        },
        get canSubmitPage() {
            return this.writeKey && this.page.hero_title && this.page.hero_subtitle && this.page.content;
        },

        // ---------- small helpers ----------

        setStatus(form, message, type = '') {
            if (form === 'page') {
                this.pageStatus = message;
                this.pageStatusType = type;
            } else if (form === 'blog') {
                this.blogStatus = message;
                this.blogStatusType = type;
            } else if (form === 'project') {
                this.projectStatus = message;
                this.projectStatusType = type;
            } else if (form === 'skills') {
                this.skillsStatus = message;
                this.skillsStatusType = type;
            } else if (form === 'socials') {
                this.socialsStatus = message;
                this.socialsStatusType = type;
            }
        },

        authHeaders(extra = {}) {
            return { 'X-Write-Key': this.writeKey, ...extra };
        },

        async apiFetch(url, options = {}) {
            const res = await fetch(url, options);
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                const message = err.detail || res.statusText || `HTTP ${res.status}`;
                throw new Error(message);
            }
            return res.status === 204 ? null : res.json();
        },

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

        // ---------- page: load / save ----------

        async loadPage() {
            try {
                const res = await fetch('/api/page/raw');
                if (res.ok) {
                    const data = await res.json();
                    this.page.hero_title = data.hero_title || '';
                    this.page.hero_subtitle = data.hero_subtitle || '';
                    this.page.content = data.content || '';
                    this.pageExists = true;
                } else if (res.status === 404) {
                    this.page = { hero_title: '', hero_subtitle: '', content: '' };
                    this.pageExists = false;
                } else {
                    this.setStatus('page', 'Failed to load page content', 'error');
                }
            } catch (e) {
                this.setStatus('page', 'Network error loading page', 'error');
            }
        },

        async savePage() {
            this.setStatus('page', 'Saving...');
            const method = this.pageExists ? 'PUT' : 'POST';

            try {
                await this.apiFetch('/api/page', {
                    method,
                    headers: this.authHeaders({ 'Content-Type': 'application/json' }),
                    body: JSON.stringify({
                        hero_title: this.page.hero_title,
                        hero_subtitle: this.page.hero_subtitle,
                        content: this.page.content,
                    }),
                });
                this.setStatus('page', 'Saved', 'success');
                this.pageExists = true;
            } catch (e) {
                this.setStatus('page', 'Error: ' + e.message, 'error');
            }
        },

        async previewPage() {
            this.pagePreview = this.renderMarkdown(this.page.content);
        },

        async loadManage() {
            this.manageError = null;
            try {
                const [bp, pp, sp, socp] = await Promise.all([
                    fetch('/api/blog'),
                    fetch('/api/project'),
                    fetch('/api/skills'),
                    fetch('/api/socials')
                ]);

                if (bp.ok) this.posts = await bp.json();
                else this.manageError = { ...this.manageError, posts: 'Failed to load posts' };

                if (pp.ok) this.projectsList = await pp.json();
                else this.manageError = { ...this.manageError, projects: 'Failed to load projects' };

                if (sp.ok) this.skills = await sp.json();
                if (socp.ok) this.socials = await socp.json();
            } catch (e) {
                this.manageError = { posts: 'Network error', projects: 'Network error' };
            }
        },

        async refreshManageIfVisible() {
            if (this.tab === 'manage') await this.loadManage();
        },

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

        // ---------- skills: load / create / update / delete ----------

        async loadSkills() {
            try {
                this.skills = await this.apiFetch('/api/skills');
            } catch (e) {
                console.error('Failed to load skills', e);
            }
        },

        startEditSkill(skill) {
            this.editingSkillId = skill.id;
            this.newSkill = skill.name;
            this.newSkillCategory = skill.category || '';
            this.newSkillLevel = skill.level || '';
        },

        cancelEditSkill() {
            this.editingSkillId = null;
            this.newSkill = '';
            this.newSkillCategory = '';
            this.newSkillLevel = '';
        },

        async saveSkill() {
            if (!this.newSkill.trim()) return;
            const isEdit = Boolean(this.editingSkillId);
            const endpoint = isEdit ? `/api/skills/${this.editingSkillId}` : '/api/skills';
            const method = isEdit ? 'PUT' : 'POST';

            try {
                await this.apiFetch(endpoint, {
                    method,
                    headers: this.authHeaders({ 'Content-Type': 'application/json' }),
                    body: JSON.stringify({
                        name: this.newSkill,
                        category: this.newSkillCategory || null,
                        level: this.newSkillLevel || null
                    })
                });
                this.setStatus('skills', isEdit ? 'Skill updated' : 'Skill added', 'success');
                this.cancelEditSkill();
                await this.loadSkills();
            } catch (e) {
                this.setStatus('skills', 'Error: ' + e.message, 'error');
            }
        },

        async deleteSkill(id) {
            if (!confirm('Delete this skill?')) return;
            try {
                await this.apiFetch(`/api/skills/${id}`, {
                    method: 'DELETE',
                    headers: this.authHeaders(),
                });
                this.setStatus('skills', 'Skill deleted', 'success');
                await this.loadSkills();
            } catch (e) {
                this.setStatus('skills', 'Delete failed: ' + e.message, 'error');
            }
        },

        // ---------- socials: load / create / update / delete ----------

        async loadSocials() {
            try {
                this.socials = await this.apiFetch('/api/socials');
            } catch (e) {
                console.error('Failed to load socials', e);
            }
        },

        startEditSocial(social) {
            this.editingSocialId = social.id;
            this.newSite = social.site;
            this.newLink = social.link;
            this.newIcon = social.icon;
        },

        cancelEditSocial() {
            this.editingSocialId = null;
            this.newSite = '';
            this.newLink = '';
            this.newIcon = '';
        },

        async saveSocial() {
            if (!this.newSite.trim() || !this.newLink.trim() || !this.newIcon.trim()) return;
            const isEdit = Boolean(this.editingSocialId);
            const endpoint = isEdit ? `/api/socials/${this.editingSocialId}` : '/api/socials';
            const method = isEdit ? 'PUT' : 'POST';

            try {
                await this.apiFetch(endpoint, {
                    method,
                    headers: this.authHeaders({ 'Content-Type': 'application/json' }),
                    body: JSON.stringify({
                        site: this.newSite,
                        link: this.newLink,
                        icon: this.newIcon
                    })
                });
                this.setStatus('socials', isEdit ? 'Social updated' : 'Social added', 'success');
                this.cancelEditSocial();
                await this.loadSocials();
            } catch (e) {
                this.setStatus('socials', 'Error: ' + e.message, 'error');
            }
        },

        async deleteSocial(id) {
            if (!confirm('Delete this social link?')) return;
            try {
                await this.apiFetch(`/api/socials/${id}`, {
                    method: 'DELETE',
                    headers: this.authHeaders(),
                });
                this.setStatus('socials', 'Social deleted', 'success');
                await this.loadSocials();
            } catch (e) {
                this.setStatus('socials', 'Delete failed: ' + e.message, 'error');
            }
        }
    };
}