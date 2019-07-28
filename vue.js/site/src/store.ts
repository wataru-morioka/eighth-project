import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    userName: 'wataru',
  },
  mutations: {
    setUser(state, payload) {
      state.userName = payload.name;
    },

  },
  actions: {
    async test({ commit, state, rootState })  {
      await axios('http://flask.site:80/user')
      .then((res) => {
        commit('setUser', {
          name: res.data.name,
        });
      });
    },

  },
  getters: {
    getName: (state, getters) => () => {
      return state.userName;
    },
  },
});
