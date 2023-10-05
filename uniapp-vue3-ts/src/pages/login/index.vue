<template>
	<view class="container">
		<image class="logo" src="/static/logo.png"></image>

		<text class="title">
			{{title}}
		</text>

		<text class="sub-title">
			{{subTitle}}
		</text>

		<!-- #ifdef MP-WEIXIN -->
		<view class="mp-weixin-login-btn-box" @tap="handleMpWeixinLogin()">
			<text class="mp-weixin-login-btn">
				小程序登录
			</text>
		</view>
		<!-- #endif -->

		<!-- #ifndef MP-WEIXIN -->
		<view class="mp-weixin-login-btn-box" @tap="handleWechatLogin()">
			<text class="mp-weixin-login-btn">
				微信登录
			</text>
		</view>
		<!-- #endif -->

		<text class="visitor-login" @tap="handleVisitorLogin()">随便逛逛</text>

		<view>
			<!-- 联系我们 -->
			<view class="cu-modal" :class="wechatQrcodeShow?'show':''">
				<view class="cu-dialog">
					<view class="cu-bar bg-white justify-end">
						<view class="action" @tap="handleWechatQrcodeShow(false)">
							<text class="cuIcon-close text-red"></text>
						</view>
					</view>
					<view class="padding-xl">
						<view style="display: flex; justify-content: center; align-items: center;">
							<image style="width: 180px; height: 180px; background-color: #eeeeee;" mode="aspectFill"
								:src="'data:image/png;base64,' + wechatQrcodeUrl"></image>
						</view>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup lang="ts">
	import { ref, onMounted } from 'vue';
	import accountRequest from '@/api/account';
	import Fingerprint2 from 'fingerprintjs2';

	const X_TOKEN = 'x-token';
	const app = getApp();

	const title = ref('欢迎使用***');
	const subTitle = ref('*******************');
	const wechatQrcodeShow = ref(false);
	const wechatQrcodeUrl = ref(null);
	const wechatIntervalId = ref(null);
	const loginLoading = ref(false);

	onMounted(() => {
		// 是否有保存登录的token
		let storageToken = uni.getStorageSync(X_TOKEN);
		if (storageToken) {
			loginSucessByToken(storageToken);
		}
	});

    /**
	 * 微信登录
	 * 微信内部以浏览器的方式打开可以直接通过页面跳转来实现登录
	 * 其他方式需要用户来扫描二维码来实现登录
	 */
	const handleWechatLogin = () => {
		let that = this
		if (wechatIntervalId.value) {
			clearInterval(wechatIntervalId.value);
			wechatIntervalId.value = null;
		}
		// 判断是否是在微信内打开，如果微信内打开则直接授权，如果不是就弹出二维码扫描
		if (/MicroMessenger/.test(navigator.userAgent)) {
			// 如果是在微信浏览器内打开，执行相关逻辑
			accountRequest.wechatUrlGet().then(data => {
				let redirectUrl = data.data
				window.location.href = redirectUrl;
			})
		} else {
			// 如果不是在微信浏览器内打开，弹出扫描二维码，扫描登录
			accountRequest.wechatQrcodeUrl().then(data => {
				data = data.data
				wechatQrcodeUrl.value = data.base64
				let wechatState = data.state
			
			    handleWechatQrcodeShow(true);
				
				// 通过轮询的方式检查state是否已经在手机端登录成功了
				wechatIntervalId.value = setInterval(() => {
					accountRequest.wechatLogin({
						state: wechatState
					}).then(data => {
						console.log(data)
						if (data.status === 'SUCCESS' && data.data) {
							clearInterval(wechatIntervalId.value);
							loginSucessByToken(data.data)
						}
					});
				}, 3000);

				// 如果连续5分钟都没有成功登录，则结束轮询
				setTimeout(() => {
					clearInterval(wechatIntervalId.value);
					console.log('WeChat login timed out.');
				}, 5 * 60 * 1000);
			});
		}
	}

    /**
	 * 小程序登录
	 */
	const handleMpWeixinLogin = () => {
		if (loginLoading.value) {
			return;
		}
		// 在小程序中获取登录凭证 code
		loginLoading.value = true;
		uni.login({
			success: (res) => {
				const code = res.code;
				accountRequest.wechatMPLogin({
					code: code,
				})
					.then(data => {
						loginSuccess(data);
					})
					.finally(() => {
						loginLoading.value = false;
					});
			},
			fail: (err) => {
				console.error(err);
			}
		});
	};

	/**
	 * 游客登录
	 */
	const handleVisitorLogin = () => {
		if (loginLoading.value) {
			return;
		}
		// 获取设备指纹
		loginLoading.value = true;
		Fingerprint2.get((components) => {
			const values = components.map(component => component.value);
			const fingerprint = Fingerprint2.x64hash128(values.join(''), 31);

			// 在这里可以将设备指纹发送到服务器进行处理
			console.log('设备指纹:', fingerprint);
			accountRequest.visitorLogin({
				fingerprint: fingerprint
			}).then(data => {
				loginSuccess(data)
			}).finally(() => {
				loginLoading.value = false;
			});
		});
	};

	/**
	 * 用户登录请求结果处理
	 */
	const loginSuccess = (data : any) => {
		if (data.code !== '200') {
			uni.showToast({
				title: data.message,
				icon: 'none'
			});
			return;
		}
		let storageToken = data.data;
		loginSucessByToken(storageToken);
	};

	/**
	 * 通过用户token加载后续逻辑
	 */
	const loginSucessByToken = (storageToken : string) => {
		uni.setStorageSync('x-token', storageToken);
		uni.switchTab({
			url: '/pages/index/index'
		});
	};

	/**
	 * 微信二维码显示
	 */
	const handleWechatQrcodeShow = (status:boolean) => {
		wechatQrcodeShow.value = status;
	};
</script>
<style scoped lang="less">
	.container {
		padding: 380rpx 48rpx 0 48rpx;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;

		.logo {
			width: 120rpx;
			height: 120rpx;
		}

		.title {
			margin-top: 60rpx;
			width: 430rpx;
			height: 67rpx;
			font-size: 48rpx;
			font-weight: 600;
			color: #000000;
			line-height: 67rpx;
			letter-spacing: 1px;
		}

		.sub-title {
			margin-top: 20rpx;
			margin-bottom: 160rpx;
			width: 390rpx;
			height: 45rpx;
			font-size: 32rpx;
			color: #939193;
			line-height: 45rpx;
			letter-spacing: 1px;
		}

		.mp-weixin-login-btn-box {
			width: 100%;
			height: 90rpx;
			border-radius: 60rpx;
			background-color: #5456EB;
			display: flex;
			align-items: center;
			justify-content: center;

			.mp-weixin-login-btn {
				color: #fff;
				font-size: 32rpx;
				font-weight: 400;
				height: 45rpx;
				line-height: 45rpx;
			}
		}

		.visitor-login {
			margin-top: 40rpx;
			height: 45rpx;
			font-size: 32rpx;
			font-weight: 400;
			color: #6236FF;
			line-height: 45rpx;
			letter-spacing: 1px;
		}
	}
</style>