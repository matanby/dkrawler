new Vue({
    el: '#app',

    data: {
        seeds: [],
        searchCriteria: ""
    },

    ready: function() {
        app = this;
        this.fetchSeeds();
    },

    methods: {
        fetchSeeds: function() {
            var url = '/seeds?' + "filter=" + app.$data.searchCriteria;
            $.getJSON(url, function(result) {
                app.$set('seeds', result.data);
                //app.$data.seeds.push({bad: true});
            });
        },

        searchCriteriaChanged: function() {
            console.log(app.$data.searchCriteria);
            app.fetchSeeds();
        }
    }
});



