from rest_framework import serializers
from .models import DonationCampaign, DonationTier, Donation


class DonationTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationTier
        fields = '__all__'


class DonationCampaignSerializer(serializers.ModelSerializer):
    tiers = DonationTierSerializer(many=True, read_only=True)
    raised_amount = serializers.ReadOnlyField()
    percent_achieved = serializers.ReadOnlyField()

    class Meta:
        model = DonationCampaign
        fields = '__all__'
        read_only_fields = ['raised_amount', 'created_at', 'slug']


class DonationSerializer(serializers.ModelSerializer):
    ussd_instructions = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = '__all__'
        read_only_fields = ['status', 'transaction_reference', 'donor', 'created_at', 'completed_at', 'currency']

    def get_ussd_instructions(self, obj):
        if obj.method == 'mobile_money' and obj.mobile_provider:
            instructions = {
                'ezypesa': 'Dial *150*02# and follow the prompts. Merchant ID: 889900',
                'airtel_money': 'Dial *150*60# and follow the prompts. Business Number: 445566',
                'mpesa': 'Send via M-Pesa. Reference: ZANCHANGEMAKERS',
            }
            return instructions.get(obj.mobile_provider, 'Follow your mobile money provider instructions.')
        return None

    def validate(self, data):
        if data.get('method') == 'mobile_money' and not data.get('mobile_provider'):
            raise serializers.ValidationError({'mobile_provider': 'Mobile provider is required for mobile money payments.'})
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['donor'] = request.user
        if validated_data.get('is_anonymous'):
            validated_data['donor_name'] = 'Anonymous'
        return super().create(validated_data)


class ConfirmDonationSerializer(serializers.Serializer):
    transaction_reference = serializers.CharField(max_length=100)
