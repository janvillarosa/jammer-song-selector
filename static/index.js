const api_endpoint = '/api/v1/';
const sleep = (milliseconds) => {
    return new Promise(resolve => setTimeout(resolve, milliseconds))
}
var animateButton = function(e) {
    e.preventDefault;
    //reset animation
    e.target.classList.remove('animate');
    
    e.target.classList.add('animate');
    setTimeout(function(){
      e.target.classList.remove('animate');
    },700);
  };
  
  var bubblyButtons = document.getElementsByClassName("bubbly-button");
  
  for (var i = 0; i < bubblyButtons.length; i++) {
    bubblyButtons[i].addEventListener('click', animateButton, false);
  }

const vm = new Vue({
    el: '#vm',
    delimiters: ['[[', ']]'],
    data: {
        track_data: null,
        artist: [],
        preview_track: null,
        vote_type: null,
        vote_message: "",
        preview_track: null,
        page_step: "start",
        jammer_songs: [],
        preloaded_track: null
    },
    mounted: async function(){
    },
    methods: {
        async get_started(){
            await this.load_track();
            this.page_step="music";
            this.play_preview_track();
            await this.clear_session();
        },
        form_artists_string(artists){
            let artist_str = "";
            for(let artist of artists){
                artist_str = artist_str + artist + ", ";
            }
            artist_str = artist_str.slice(0, -2);
            return artist_str;
        },
        async preload_next_track(){
            //Already load next track so it's faster
            //This will be very useful if the user is running all possible songs and is getting duplicate random songs
            this.preloaded_track = await fetch(api_endpoint + 'song/random');
        },
        async load_track(){
            let song_data = null;
            if(this.preloaded_track == null){
                const response = await fetch(api_endpoint + 'song/random');
                song_data = await response.json();
            } else {
                song_data = await this.preloaded_track.json();
            }
            this.track_data = song_data;
            this.artist = this.form_artists_string(song_data.artists);
            this.vote_type = null;
            this.vote_message =  "";
            this.preview_track = song_data.preview_url;
            this.preload_next_track();
        },
        async vote_jammer(){
            const response = await fetch(api_endpoint + 'vote/jammer/' + this.track_data.id, {method: 'POST'});
            const res_json = await response.json();
            await this.show_vote_message("jammer", res_json.jammer, res_json.not_jammer);
            
            old_track = this.track_data;
            old_track.spotify_url = "https://open.spotify.com/track/" + old_track.id;
            old_track.artist_str = this.artist;
            
            this.$refs.audio.pause();
            await this.load_track();
            this.play_preview_track();
            this.jammer_songs.push(old_track);
        },
        async vote_nojammer(){
            const response = await fetch(api_endpoint + 'vote/not_jammer/'+ this.track_data.id, {method: 'POST'});
            const res_json = await response.json();
            await this.show_vote_message("not_jammer", res_json.jammer, res_json.not_jammer);
            this.$refs.audio.pause();
            await this.load_track();
            this.play_preview_track();
        },
        async show_vote_message(vote_type, jammer_count, not_jammer_count) {
            const jammer_message = " of listeners also thought this was a great song!";
            const not_jammer_message = " of listeners also didn't think it was a jam";
            const total_votes = jammer_count + not_jammer_count;
            let vote_percentage = 0
            if(vote_type == "jammer"){
                vote_percentage = (jammer_count / total_votes * 100).toFixed();
                this.vote_message = "🔥 " + vote_percentage.toString() + "%" + jammer_message;
            } else {
                vote_percentage = (not_jammer_count / total_votes * 100).toFixed();
                this.vote_message = "👎" + vote_percentage.toString() + "%" + not_jammer_message;
            }
            this.vote_type = vote_type;
            await sleep(1000);
        },
        async clear_session(){
            await fetch(api_endpoint + 'vote/clear_session', {method: 'POST'});
        },
        async play_preview_track(){
            if(this.page_step != "music"){
                this.$refs.audio.volume = 0.0;
                await this.$refs.audio.pause();
                return
            }
            if(this.preview_track == null){
                return
            }
            this.$refs.audio.volume = 0.0;
            this.$refs.audio.pause();
            
            this.$refs.audio.src = this.preview_track;
            this.$refs.audio.load();
            this.$refs.audio.play();
            this.$refs.audio.volume = 0.5;
        },
        async generate_all_jammers(){
            this.$refs.audio.pause();
            this.page_step="show_jams";
            await this.$refs.audio.pause();
            this.$refs.audio.volume = 0.0;
        },
        start_over(){
            this.vote_type = null;
            this.vote_message =  "";
            this.page_step = "start";
            this.jammer_songs = [];
            this.$refs.audio.src = null;
        }
    }
})