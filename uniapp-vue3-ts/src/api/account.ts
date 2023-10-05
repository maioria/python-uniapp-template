import request from "@/axios/api";
export default {
	wechatUrlGet: () => {
		return request('/wechat/redirect-url', 'GET', null, true);
	},
	wechatQrcodeUrl: () => {
		return request('/wechat/qrcode-url', 'GET', null, true);
	},
	wechatMPLogin: (data : any) => {
		return request("/wechat/code-login", "POST", data, true);
	},
	wechatLogin: (data : any) => {
		return request("/wechat/code-login", "POST", data, false);
	},
	visitorLogin: (data : any) => {
		return request("/visitor-login", "POST", data, true);
	},
	phoneLogin: (data : any) => {
		return request('/phone-login', 'POST', data, true);
	},
	accountInfoGet: () => {
		return request("/account-info", "GET", null);
	},
};