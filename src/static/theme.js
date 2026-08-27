function themeMixin() {
    return {
        theme: localStorage.getItem('theme')
            || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'),

        initTheme() {
            document.documentElement.setAttribute('data-theme', this.theme);

            this.$watch('theme', (value, oldValue) => {
                if (value === oldValue) return;
                localStorage.setItem('theme', value);
                document.documentElement.setAttribute('data-theme', value);
            });

            window.addEventListener('storage', (e) => {
                if (e.key === 'theme' && e.newValue && e.newValue !== this.theme) {
                    this.theme = e.newValue;
                }
            });
        },

        toggleTheme() {
            this.theme = this.theme === 'dark' ? 'light' : 'dark';
        },
    };
}