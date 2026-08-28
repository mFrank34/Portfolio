function homeApp() {
    return {
        ...themeMixin(),
        page: null,
        socials: [],
        skills: [],
        projects: [],
        posts: [],
        loading: true,
        async init() {
            this.initTheme();
            try {
                const [page, socials, skills, projects, posts] = await Promise.all([
                    fetch('/api/page').then(r => r.ok ? r.json() : null),
                    fetch('/api/socials').then(r => r.json()),
                    fetch('/api/skills').then(r => r.json()),
                    fetch('/api/project').then(r => r.json()),
                    fetch('/api/blog').then(r => r.json()),
                ]);
                this.page = page;
                this.socials = socials;
                this.skills = skills;
                this.projects = projects;
                this.posts = posts;
            } catch (e) {
                console.error('Failed to load home page data', e);
            } finally {
                this.loading = false;
            }
        },
        renderMarkdown(content) {
            if (!content) return '';
            return typeof marked !== 'undefined' ? marked.parse(content) : content;
        },
        get formattedUpdatedAt() {
            if (!this.page?.updated_at) return '';
            return new Date(this.page.updated_at).toLocaleDateString(undefined, {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
            });
        }
    };
}