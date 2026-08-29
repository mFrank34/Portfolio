function projectApp() {
    return {
        ...themeMixin(),
        project: null,
        loading: true,
        async init() {
            this.initTheme();
            const slug = window.location.pathname.split('/').filter(Boolean).pop();
            try {
                const res = await fetch('/api/project/' + slug);
                if (res.ok) {
                    this.project = await res.json();
                }
            } catch (e) {
                console.error('Failed to load project', e);
            } finally {
                this.loading = false;
            }
        }
    };
}