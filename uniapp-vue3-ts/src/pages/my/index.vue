<template>
	<view class="my-container">
		<CommonHeader class="header" title="Talkie">
			<template v-slot:content>
				<text>个人中心</text>
			</template>
		</CommonHeader>
		<view class="mine-content">
			<!-- profile -->
			<view class="profile-box">
				<view v-if="accountInfo.account_id.indexOf('visitor') === 0" class="profile" @tap="hangleLogin">
					<image class="profile-avatar" src="/static/img/default/avatar.jpg" />
					<text class="profile-name">请登录</text>
				</view>
				<view v-else class="profile">
					<image class="profile-avatar" :src="accountInfo.head_img?accountInfo.head_img:'/static/img/default/avatar.png'" />
					<text class="profile-name">{{ accountInfo.nickname?accountInfo.nickname:accountInfo.account_id }}</text>
				</view>
			</view>
			<view class="setting">
				<view class="setting-card" @tap="goFeedback">
					<image class="setting-card-logo" src="/static/img/icons/feedback.png" />
					<text class="setting-card-title">反馈</text>
				</view>
				<view class="setting-card" @tap="goGithub">
					<image class="setting-card-logo" src="/static/img/github/github-mark.png" />
					<text class="setting-card-title">Github</text>
				</view>
				<!-- 如果是小程序登录 -->
				<view v-if="accountInfo.account_id.indexOf('visitor') < 0" class="setting-card" @tap="hangleLogout">
					<image class="setting-card-logo" src="/static/img/icons/feedback.png" />
					<text class="setting-card-title">退出登录</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup lang="ts">
import CommonHeader from "@/components/CommonHeader.vue";
import { ref, reactive, onMounted } from "vue";
import accountRequest from '@/api/account';
import type { AccountInfo } from '@/models/index';


const accountInfo = ref<AccountInfo>({ account_id: '', head_img: null, nickname: null });

onMounted(() => {
	accountRequest.accountInfoGet().then((data) => {
		accountInfo.value = data.data;
	});
	uni.setNavigationBarTitle({
		title: '个人中心'
	});
});

const goGithub = () => {
	const redirectUrl = 'https://github.com/maioria/python-uniapp-template/issues';
	// #ifdef H5
	window.open(redirectUrl);
	// #endif

	// 非h5的情况提示用户访问
	// #ifndef H5
	uni.showToast({
		title: '可通过github访问 python-uniapp-template',
		icon: 'none'
	})
	// #endif
}

const hangleLogout = () => {
	uni.showModal({
		title: '提示',
		content: '确定退出登录吗？',
		confirmColor: '#6236ff',
		success: function (res) {
			if (res.confirm) {
				uni.removeStorageSync('x-token');
				uni.reLaunch({
					url: '/pages/login/index'
				})
			} else if (res.cancel) {
				console.log('用户点击取消');
			}
		}
	});
}

const hangleLogin = () => {
	uni.removeStorageSync('x-token');
	uni.reLaunch({
		url: '/pages/login/index'
	})
}

const goFeedback = () => {
	uni.navigateTo({
		url: '/pages/feedback/index'
	})
}
</script>
<style scoped src="./less/index.less" lang="less"></style>
